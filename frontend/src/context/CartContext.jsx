import { createContext, useContext, useState } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [cart, setCart] = useState([]);

  const addToCart = (product) => {
    setCart(prev => {
      const existingItem = prev.find(item => item.id === product.id);
      const quantityToAdd = product.quantity || 1;
      
      if (existingItem) {
        // Nếu sản phẩm đã có trong giỏ, tăng quantity
        return prev.map(item =>
          item.id === product.id ? { ...item, quantity: item.quantity + quantityToAdd } : item
        );
      }
      // Nếu sản phẩm chưa có, thêm mới với quantity từ product
      return [...prev, { ...product, quantity: quantityToAdd }];
    });
  };

  const updateQuantity = (id, quantity) => {
    setCart(prev => {
      if (quantity <= 0) {
        return prev.filter(item => item.id !== id);
      }
      return prev.map(item =>
        item.id === id ? { ...item, quantity } : item
      );
    });
  };

  const removeFromCart = (id) => {
    setCart(prev => prev.filter(item => item.id !== id));
  };

  const clearCart = () => setCart([]);

  // Danh sách tên sản phẩm trong giỏ (dùng cho trang gợi ý)
  const cartNames = cart.map(item => item.name.toUpperCase());

  return (
    <CartContext.Provider value={{ cart, cartNames, addToCart, updateQuantity, removeFromCart, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
