"""
数据导入服务 - 标准化的数据导入接口
支持Excel/CSV文件导入商品数据
"""
import pandas as pd
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
import re

from database.db_manager import get_db_context
from database.crud import ImportBatchCRUD, ProductCRUD, RawProductDataCRUD
from database.models import ProductDB


class DataImportService:
    """数据导入服务"""

    def __init__(self):
        self.batch_crud = None
        self.product_crud = None
        self.raw_data_crud = None

    def _detect_resource_type(self, url: str) -> str:
        """检测资源类型"""
        if 'baidu.com' in url or 'pan.baidu.com' in url:
            return 'baidu_pan'
        elif 'quark.cn' in url or 'pan.quark.cn' in url:
            return 'quark'
        elif 'aliyun.com' in url or 'alywp.net' in url:
            return 'aliyun'
        elif '189.cn' in url:
            return 'tianyi'
        elif 'lanzouo.com' in url or 'lzpan.com' in url:
            return 'lanzou'
        else:
            return 'unknown'

    def _parse_dataframe_row(self, row: pd.Series, column_mapping: Dict[str, str]) -> Dict:
        """
        解析DataFrame行，转换为商品数据

        column_mapping格式:
        {
            'external_id': 'id列名',
            'title_zh': '资源名称列名',
            'resource_url': '资源链接列名',
            'created_at': '创建时间列名',
        }
        """
        product_data = {
            'product_id': str(uuid.uuid4()),
            'title_en': '',  # 默认值
            'category': '课程资源',  # 默认分类
            'price_usd': 0.0,  # 默认价格
            'avg_rating': 0.0,  # 默认评分
            'monthly_sales': 0,  # 默认销量
            'main_market': 'CN',  # 默认市场
            'tags': '',
        }

        # 根据映射提取数据
        for target_field, source_col in column_mapping.items():
            if source_col in row.index and pd.notna(row[source_col]):
                value = row[source_col]

                # 处理日期
                if target_field == 'created_at' and isinstance(value, str):
                    try:
                        value = pd.to_datetime(value)
                    except:
                        value = datetime.utcnow()
                elif isinstance(value, pd.Timestamp):
                    value = value.to_pydatetime()

                product_data[target_field] = value

        # 自动检测资源类型
        if 'resource_url' in product_data and product_data['resource_url']:
            product_data['resource_type'] = self._detect_resource_type(product_data['resource_url'])

        # 使用中文名称作为描述
        if 'title_zh' in product_data and product_data['title_zh']:
            product_data['description'] = product_data['title_zh']

        return product_data

    def import_from_excel(
        self,
        file_path: str,
        sheet_name: int = 0,
        column_mapping: Optional[Dict[str, str]] = None,
        batch_name: Optional[str] = None,
        skip_duplicates: bool = True,
        update_existing: bool = False
    ) -> Dict:
        """
        从Excel文件导入数据

        Args:
            file_path: Excel文件路径
            sheet_name: 工作表索引或名称
            column_mapping: 列名映射字典
            batch_name: 批次名称
            skip_duplicates: 是否跳过重复数据
            update_existing: 是否更新已存在的数据

        Returns:
            导入结果字典
        """
        # 自动检测列映射
        if column_mapping is None:
            column_mapping = self._auto_detect_columns(file_path, sheet_name)

        # 读取Excel
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        return self._import_dataframe(
            df=df,
            column_mapping=column_mapping,
            batch_name=batch_name or f"Import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            source_file=file_path,
            skip_duplicates=skip_duplicates,
            update_existing=update_existing
        )

    def import_from_csv(
        self,
        file_path: str,
        column_mapping: Optional[Dict[str, str]] = None,
        batch_name: Optional[str] = None,
        skip_duplicates: bool = True,
        update_existing: bool = False,
        encoding: str = 'utf-8'
    ) -> Dict:
        """
        从CSV文件导入数据

        Args:
            file_path: CSV文件路径
            column_mapping: 列名映射字典
            batch_name: 批次名称
            skip_duplicates: 是否跳过重复数据
            update_existing: 是否更新已存在的数据
            encoding: 文件编码

        Returns:
            导入结果字典
        """
        # 自动检测列映射
        if column_mapping is None:
            column_mapping = self._auto_detect_columns_csv(file_path, encoding)

        # 读取CSV
        df = pd.read_csv(file_path, encoding=encoding)

        return self._import_dataframe(
            df=df,
            column_mapping=column_mapping,
            batch_name=batch_name or f"Import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            source_file=file_path,
            skip_duplicates=skip_duplicates,
            update_existing=update_existing
        )

    def _auto_detect_columns(self, file_path: str, sheet_name: int = 0) -> Dict[str, str]:
        """自动检测Excel列映射"""
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1)
        return self._detect_columns_from_dataframe(df)

    def _auto_detect_columns_csv(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, str]:
        """自动检测CSV列映射"""
        df = pd.read_csv(file_path, encoding=encoding, nrows=1)
        return self._detect_columns_from_dataframe(df)

    def _detect_columns_from_dataframe(self, df: pd.DataFrame) -> Dict[str, str]:
        """从DataFrame检测列映射"""
        columns = df.columns.tolist()
        mapping = {}

        # 常见列名模式
        patterns = {
            'external_id': ['id', '编号', 'ID', '序号', '资源ID', '资源编号'],
            'title_zh': ['资源名称', '名称', '标题', '商品名称', '课程名称', 'title', 'name'],
            'resource_url': ['资源链接', '链接', 'url', 'URL', '地址', '下载地址', '网盘地址'],
            'created_at': ['创建时间', '时间', '日期', '创建日期', 'date', 'time', 'created']
        }

        # 模糊匹配列名
        for target_field, pattern_list in patterns.items():
            for col in columns:
                for pattern in pattern_list:
                    if pattern.lower() in str(col).lower():
                        mapping[target_field] = col
                        break
                if target_field in mapping:
                    break

        return mapping

    def _import_dataframe(
        self,
        df: pd.DataFrame,
        column_mapping: Dict[str, str],
        batch_name: str,
        source_file: str,
        skip_duplicates: bool,
        update_existing: bool
    ) -> Dict:
        """导入DataFrame数据"""
        with get_db_context() as session:
            self.batch_crud = ImportBatchCRUD(session)
            self.product_crud = ProductCRUD(session)
            self.raw_data_crud = RawProductDataCRUD(session)

            # 创建导入批次
            batch = self.batch_crud.create_batch({
                'batch_name': batch_name,
                'source_file': source_file,
                'total_records': len(df),
                'status': 'processing'
            })

            success_count = 0
            failed_count = 0
            skipped_count = 0
            errors = []

            # 收集原始数据记录（用于批量写入）
            raw_data_records = []

            try:
                for idx, row in df.iterrows():
                    try:
                        # 解析数据
                        product_data = self._parse_dataframe_row(row, column_mapping)

                        # 检查是否已存在
                        existing = None
                        if product_data.get('external_id'):
                            existing = self.batch_crud.get_product_by_external_id(product_data['external_id'])

                        # 保存完整原始数据（JSON格式）
                        import json
                        from datetime import datetime

                        def json_serial(obj):
                            """JSON序列化处理器，处理datetime等特殊类型"""
                            if isinstance(obj, datetime):
                                return obj.isoformat()
                            elif hasattr(obj, 'isoformat'):
                                return obj.isoformat()
                            raise TypeError(f'Type {type(obj)} not serializable')

                        raw_data_record = {
                            'external_id': product_data.get('external_id', ''),
                            'raw_data': json.dumps(row.to_dict(), ensure_ascii=False, default=json_serial),
                            'source_file': source_file,
                            'source_row': idx + 2,  # Excel行号（含表头）
                        }

                        if existing:
                            if skip_duplicates and not update_existing:
                                skipped_count += 1
                                continue
                            elif update_existing:
                                # 更新现有商品
                                for key, value in product_data.items():
                                    if hasattr(existing, key) and key != 'product_id':
                                        setattr(existing, key, value)
                                session.commit()

                                # 同时更新原始数据
                                existing_raw = self.raw_data_crud.get_raw_data_by_external_id(product_data['external_id'])
                                if existing_raw:
                                    self.raw_data_crud.update_raw_data(product_data['external_id'], raw_data_record)
                                else:
                                    raw_data_records.append(raw_data_record)

                                success_count += 1
                            else:
                                skipped_count += 1
                        else:
                            # 创建新商品
                            new_product = ProductDB(**product_data)
                            session.add(new_product)
                            session.commit()

                            # 添加原始数据记录
                            raw_data_records.append(raw_data_record)

                            success_count += 1

                    except Exception as e:
                        failed_count += 1
                        errors.append(f"行 {idx + 2}: {str(e)}")

                # 批量写入原始数据
                if raw_data_records:
                    self.raw_data_crud.bulk_create_raw_data(raw_data_records)

                # 更新批次状态
                self.batch_crud.update_batch(batch.id, {
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'skipped_count': skipped_count,
                    'status': 'completed' if failed_count == 0 else 'partial_success',
                    'error_message': '\n'.join(errors[:10]) if errors else None,
                    'completed_at': datetime.utcnow()
                })

                return {
                    'batch_id': batch.id,
                    'total_records': len(df),
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'skipped_count': skipped_count,
                    'status': 'completed' if failed_count == 0 else 'partial_success',
                    'errors': errors[:10] if errors else []
                }

            except Exception as e:
                # 更新批次为失败状态
                self.batch_crud.update_batch(batch.id, {
                    'status': 'failed',
                    'error_message': str(e),
                    'completed_at': datetime.utcnow()
                })
                raise


# 导出便捷函数
def import_from_file(
    file_path: str,
    file_type: str = 'auto',
    column_mapping: Optional[Dict[str, str]] = None,
    batch_name: Optional[str] = None,
    skip_duplicates: bool = True,
    update_existing: bool = False,
    **kwargs
) -> Dict:
    """
    便捷的导入函数

    Args:
        file_path: 文件路径
        file_type: 文件类型 ('excel', 'csv', 'auto')
        column_mapping: 列名映射
        batch_name: 批次名称
        skip_duplicates: 跳过重复
        update_existing: 更新已存在
        **kwargs: 其他参数

    Returns:
        导入结果
    """
    service = DataImportService()

    # 自动检测文件类型
    if file_type == 'auto':
        if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            file_type = 'excel'
        elif file_path.endswith('.csv'):
            file_type = 'csv'
        else:
            raise ValueError(f"无法识别文件类型: {file_path}")

    if file_type == 'excel':
        return service.import_from_excel(
            file_path=file_path,
            column_mapping=column_mapping,
            batch_name=batch_name,
            skip_duplicates=skip_duplicates,
            update_existing=update_existing,
            **kwargs
        )
    elif file_type == 'csv':
        return service.import_from_csv(
            file_path=file_path,
            column_mapping=column_mapping,
            batch_name=batch_name,
            skip_duplicates=skip_duplicates,
            update_existing=update_existing,
            **kwargs
        )
    else:
        raise ValueError(f"不支持的文件类型: {file_type}")
