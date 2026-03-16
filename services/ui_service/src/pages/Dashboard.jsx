import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Button,
  Card,
  Table,
  Modal,
  Form,
  Input,
  Select,
  message,
  Tag,
  Space,
  Typography,
} from "antd";
import {
  PlusOutlined,
  EyeOutlined,
  ProjectOutlined,
  RobotOutlined,
} from "@ant-design/icons";
import { getProjects, createProject, getModels } from "../api/project";

const { Title } = Typography;

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [models, setModels] = useState({ embedding_models: [], llm_models: [] });
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const { data } = await getProjects();
      setProjects(data);
    } catch {
      message.error("Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  const fetchModels = async () => {
    try {
      const { data } = await getModels();
      setModels(data);
    } catch {
      /* models will use empty fallback */
    }
  };

  useEffect(() => {
    fetchProjects();
    fetchModels();
  }, []);

  const handleCreate = async (values) => {
    setCreating(true);
    try {
      await createProject(values);
      message.success("Project created");
      setModalOpen(false);
      form.resetFields();
      fetchProjects();
    } catch (err) {
      message.error(err.response?.data?.error || "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: "Embedding Model",
      dataIndex: "embedding_model",
      key: "embedding_model",
      render: (v) => <Tag icon={<RobotOutlined />} color="purple">{v}</Tag>,
    },
    {
      title: "LLM Model",
      dataIndex: "llm_model",
      key: "llm_model",
      render: (v) => <Tag icon={<RobotOutlined />} color="geekblue">{v}</Tag>,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (s) => (
        <Tag color={s === "active" ? "green" : "default"}>{s}</Tag>
      ),
    },
    {
      title: "Created At",
      dataIndex: "created_at",
      key: "created_at",
      render: (v) => new Date(v).toLocaleString(),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => navigate(`/projects/${record.id}`)}
        >
          View
        </Button>
      ),
    },
  ];

  return (
    <>
      <Card>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 16,
          }}
        >
          <Title level={4} style={{ margin: 0 }}>
            <ProjectOutlined /> Projects
          </Title>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalOpen(true)}
          >
            New Project
          </Button>
        </div>
        <Table
          columns={columns}
          dataSource={projects}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="Create Project"
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{
            embedding_model: "vietnamese-embedding",
            llm_model: "gpt-4o-mini",
          }}
        >
          <Form.Item
            name="name"
            label="Project Name"
            rules={[{ required: true, message: "Please enter project name" }]}
          >
            <Input placeholder="My RAG Project" />
          </Form.Item>
          <Form.Item
            name="embedding_model"
            label="Embedding Model"
            rules={[{ required: true, message: "Please select an embedding model" }]}
          >
            <Select
              placeholder="Select embedding model"
              options={models.embedding_models.map((m) => ({ value: m, label: m }))}
            />
          </Form.Item>
          <Form.Item
            name="llm_model"
            label="LLM Model"
            rules={[{ required: true, message: "Please select a LLM model" }]}
          >
            <Select
              placeholder="Select LLM model"
              options={models.llm_models.map((m) => ({ value: m, label: m }))}
            />
          </Form.Item>
          <Space style={{ width: "100%", justifyContent: "flex-end" }}>
            <Button onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit" loading={creating}>
              Create
            </Button>
          </Space>
        </Form>
      </Modal>
    </>
  );
}
