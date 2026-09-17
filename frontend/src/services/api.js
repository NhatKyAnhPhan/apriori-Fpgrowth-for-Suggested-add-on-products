import axios from "axios";

const api = axios.create({
  baseURL:         "http://localhost:5000",
  withCredentials: true,          // gửi httpOnly cookie (refresh token)
  headers: { "Content-Type": "application/json" },
});

// Response interceptor: hiển thị lỗi dạng thống nhất
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.error ||
      err.response?.data?.message ||
      "Đã xảy ra lỗi. Vui lòng thử lại.";
    return Promise.reject(new Error(message));
  }
);

export default api;
