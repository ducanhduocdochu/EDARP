import { Navigate } from "react-router-dom";
import { Spin } from "antd";
import { useAuth } from "../contexts/AuthContext";

export default function PrivateRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", paddingTop: 200 }}>
        <Spin size="large" />
      </div>
    );
  }

  return user ? children : <Navigate to="/login" replace />;
}
