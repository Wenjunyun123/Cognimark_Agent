import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  name: string;
  avatar?: string;
  email?: string;
}

interface AuthContextType {
  user: User | null;
  login: (username: string) => void;
  register: (username: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check localStorage for existing session
    const storedUser = localStorage.getItem('cognimark_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse user data', e);
        localStorage.removeItem('cognimark_user');
      }
    }
  }, []);

  const login = (username: string) => {
    // Check if user exists in registered users
    const registeredUsers = JSON.parse(localStorage.getItem('cognimark_registered_users') || '{}');
    if (!registeredUsers[username]) {
      throw new Error('用户不存在，请先注册');
    }

    // In a real app, we would verify password here
    // For this demo, we trust the registration
    const user = registeredUsers[username];
    setUser(user);
    localStorage.setItem('cognimark_user', JSON.stringify(user));
  };

  const register = (username: string) => {
    const registeredUsers = JSON.parse(localStorage.getItem('cognimark_registered_users') || '{}');
    
    if (registeredUsers[username]) {
      throw new Error('用户名已存在');
    }

    const newUser = {
      name: username,
      avatar: username.charAt(0).toUpperCase(),
      email: `${username.toLowerCase().replace(/\s+/g, '.')}@example.com`
    };

    registeredUsers[username] = newUser;
    localStorage.setItem('cognimark_registered_users', JSON.stringify(registeredUsers));
    
    // Auto login after register
    setUser(newUser);
    localStorage.setItem('cognimark_user', JSON.stringify(newUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('cognimark_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
