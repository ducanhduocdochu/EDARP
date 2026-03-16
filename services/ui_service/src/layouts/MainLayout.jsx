import { useState } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import {
  Layout,
  Menu,
  Avatar,
  Dropdown,
  Typography,
  theme,
} from "antd";
import {
  ProjectOutlined,
  TeamOutlined,
  LogoutOutlined,
  UserOutlined,
  DashboardOutlined,
} from "@ant-design/icons";
import { useAuth } from "../contexts/AuthContext";

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

export default function MainLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const { token: themeToken } = theme.useToken();

  const menuItems = [
    {
      key: "/",
      icon: <DashboardOutlined />,
      label: "Projects",
    },
    {
      key: "/users",
      icon: <TeamOutlined />,
      label: "Users",
    },
  ];

  const profileMenu = {
    items: [
      {
        key: "profile",
        icon: <UserOutlined />,
        label: `${user?.email}`,
        disabled: true,
      },
      { type: "divider" },
      {
        key: "logout",
        icon: <LogoutOutlined />,
        label: "Logout",
        danger: true,
        onClick: () => {
          logout();
          navigate("/login");
        },
      },
    ],
  };

  const selected = location.pathname === "/" ? "/" : "/" + location.pathname.split("/")[1];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{ background: themeToken.colorBgContainer }}
      >
        <div
          style={{
            height: 64,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderBottom: `1px solid ${themeToken.colorBorderSecondary}`,
          }}
        >
          <ProjectOutlined style={{ fontSize: 24, color: themeToken.colorPrimary }} />
          {!collapsed && (
            <Text strong style={{ marginLeft: 10, fontSize: 16 }}>
              Platform RAG
            </Text>
          )}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[selected]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: themeToken.colorBgContainer,
            padding: "0 24px",
            display: "flex",
            justifyContent: "flex-end",
            alignItems: "center",
            borderBottom: `1px solid ${themeToken.colorBorderSecondary}`,
          }}
        >
          <Dropdown menu={profileMenu} placement="bottomRight">
            <div style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}>
              <Avatar icon={<UserOutlined />} />
              <Text>{user?.email}</Text>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
