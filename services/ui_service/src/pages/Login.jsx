import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Form, Input, Button, Card, Typography, message, Space } from "antd";
import { LockOutlined, MailOutlined } from "@ant-design/icons";
import { login } from "../api/auth";
import { useAuth } from "../contexts/AuthContext";

const { Title, Text } = Typography;

export default function Login() {
  const [loading, setLoading] = useState(false);
  const { loginSuccess } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const { data } = await login(values);
      await loginSuccess(data);
      message.success("Login successful");
      navigate("/");
    } catch (err) {
      message.error(err.response?.data?.error || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      }}
    >
      <Card style={{ width: 400, borderRadius: 12, boxShadow: "0 8px 32px rgba(0,0,0,0.12)" }}>
        <Space direction="vertical" size="large" style={{ width: "100%", textAlign: "center" }}>
          <div>
            <Title level={2} style={{ marginBottom: 4 }}>Welcome back</Title>
            <Text type="secondary">Sign in to Platform RAG</Text>
          </div>
          <Form layout="vertical" onFinish={onFinish} size="large">
            <Form.Item
              name="email"
              rules={[
                { required: true, message: "Please enter your email" },
                { type: "email", message: "Invalid email" },
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="Email" />
            </Form.Item>
            <Form.Item
              name="password"
              rules={[{ required: true, message: "Please enter your password" }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Password" />
            </Form.Item>
            <Form.Item style={{ marginBottom: 12 }}>
              <Button type="primary" htmlType="submit" loading={loading} block>
                Sign In
              </Button>
            </Form.Item>
            <Text>
              Don't have an account? <Link to="/register">Register</Link>
            </Text>
          </Form>
        </Space>
      </Card>
    </div>
  );
}
