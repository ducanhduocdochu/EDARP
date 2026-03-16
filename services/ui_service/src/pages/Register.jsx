import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Form, Input, Button, Card, Typography, message, Space } from "antd";
import { LockOutlined, MailOutlined, BankOutlined } from "@ant-design/icons";
import { register } from "../api/auth";

const { Title, Text } = Typography;

export default function Register() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await register(values);
      message.success("Registration successful! Please login.");
      navigate("/login");
    } catch (err) {
      message.error(err.response?.data?.error || "Registration failed");
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
      <Card style={{ width: 420, borderRadius: 12, boxShadow: "0 8px 32px rgba(0,0,0,0.12)" }}>
        <Space direction="vertical" size="large" style={{ width: "100%", textAlign: "center" }}>
          <div>
            <Title level={2} style={{ marginBottom: 4 }}>Create Account</Title>
            <Text type="secondary">Register a new tenant</Text>
          </div>
          <Form layout="vertical" onFinish={onFinish} size="large">
            <Form.Item
              name="name"
              rules={[{ required: true, message: "Please enter tenant name" }]}
            >
              <Input prefix={<BankOutlined />} placeholder="Tenant / Organization name" />
            </Form.Item>
            <Form.Item
              name="email"
              rules={[
                { required: true, message: "Please enter your email" },
                { type: "email", message: "Invalid email" },
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="Admin email" />
            </Form.Item>
            <Form.Item
              name="password"
              rules={[
                { required: true, message: "Please enter your password" },
                { min: 6, message: "At least 6 characters" },
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Password" />
            </Form.Item>
            <Form.Item style={{ marginBottom: 12 }}>
              <Button type="primary" htmlType="submit" loading={loading} block>
                Register
              </Button>
            </Form.Item>
            <Text>
              Already have an account? <Link to="/login">Sign In</Link>
            </Text>
          </Form>
        </Space>
      </Card>
    </div>
  );
}
