import { createContext, useContext, useState, useEffect, useCallback } from "react";
import api from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user,        setUser]        = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [loading,     setLoading]     = useState(true);

  // Thử refresh token khi F5 trang (token lưu trong httpOnly cookie)
  useEffect(() => {
    const tryRefresh = async () => {
      try {
        const res = await api.post("/auth/refresh");
        setAccessToken(res.data.access_token);
        // Lấy thông tin user
        const me = await api.get("/auth/me", {
          headers: { Authorization: `Bearer ${res.data.access_token}` },
        });
        setUser(me.data.user);
      } catch {
        // Chưa đăng nhập — bình thường
      } finally {
        setLoading(false);
      }
    };
    tryRefresh();
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    setAccessToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  }, []);

  const register = useCallback(async (username, email, password) => {
    const res = await api.post("/auth/register", { username, email, password });
    setAccessToken(res.data.access_token);
    setUser(res.data.user);
    return res.data;
  }, []);

  const logout = useCallback(() => {
    setAccessToken(null);
    setUser(null);
  }, []);

  // Axios interceptor tự gắn token vào mọi request
  useEffect(() => {
    const interceptor = api.interceptors.request.use((config) => {
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      return config;
    });
    return () => api.interceptors.request.eject(interceptor);
  }, [accessToken]);

  return (
    <AuthContext.Provider value={{ user, accessToken, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
