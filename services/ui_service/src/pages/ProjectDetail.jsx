import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Card,
  Tabs,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Upload,
  Statistic,
  List,
  Alert,
  Divider,
  message,
  Tag,
  Space,
  Typography,
  Descriptions,
  Popconfirm,
  Tooltip,
  InputNumber,
} from "antd";
import {
  KeyOutlined,
  FileTextOutlined,
  PlusOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
  CopyOutlined,
  EditOutlined,
  RobotOutlined,
  CloudUploadOutlined,
  SearchOutlined,
  DatabaseOutlined,
  UploadOutlined,
  MessageOutlined,
  SendOutlined,
} from "@ant-design/icons";
import {
  getProject,
  getModels,
  updateProject,
  getApiKeys,
  createApiKey,
  getDocuments,
  createDocument,
  deleteDocument,
  embedText,
} from "../api/project";
import {
  indexJsonFile,
  indexText,
  searchIndex,
  getIndexStatus,
  clearIndex,
} from "../api/indexing";
import { queryRAG } from "../api/query";

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [apiKeys, setApiKeys] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState({ project: true, keys: false, docs: false });
  const [models, setModels] = useState({ embedding_models: [], llm_models: [] });
  const [editModal, setEditModal] = useState(false);
  const [editSaving, setEditSaving] = useState(false);
  const [newKeyVisible, setNewKeyVisible] = useState(null);
  const [docModal, setDocModal] = useState(false);
  const [docCreating, setDocCreating] = useState(false);
  const [embedInput, setEmbedInput] = useState("");
  const [embedResult, setEmbedResult] = useState(null);
  const [embedding, setEmbedding] = useState(false);
  const [idxStatus, setIdxStatus] = useState(null);
  const [indexing, setIndexing] = useState(false);
  const [idxTextInput, setIdxTextInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchTopK, setSearchTopK] = useState(5);
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatTopK, setChatTopK] = useState(3);
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();

  const fetchProject = async () => {
    try {
      const { data } = await getProject(id);
      setProject(data);
    } catch {
      message.error("Project not found");
      navigate("/");
    } finally {
      setLoading((p) => ({ ...p, project: false }));
    }
  };

  const fetchApiKeys = async () => {
    setLoading((p) => ({ ...p, keys: true }));
    try {
      const { data } = await getApiKeys(id);
      setApiKeys(data);
    } finally {
      setLoading((p) => ({ ...p, keys: false }));
    }
  };

  const fetchDocuments = async () => {
    setLoading((p) => ({ ...p, docs: true }));
    try {
      const { data } = await getDocuments(id);
      setDocuments(data);
    } finally {
      setLoading((p) => ({ ...p, docs: false }));
    }
  };

  const fetchModels = async () => {
    try {
      const { data } = await getModels();
      setModels(data);
    } catch {
      /* fallback empty */
    }
  };

  const fetchIndexStatus = async () => {
    try {
      const { data } = await getIndexStatus(id);
      setIdxStatus(data);
    } catch {
      setIdxStatus(null);
    }
  };

  useEffect(() => {
    fetchProject();
    fetchApiKeys();
    fetchDocuments();
    fetchModels();
    fetchIndexStatus();
  }, [id]);

  const handleEditProject = async (values) => {
    setEditSaving(true);
    try {
      const { data } = await updateProject(id, values);
      setProject(data);
      message.success("Project updated");
      setEditModal(false);
    } catch (err) {
      message.error(err.response?.data?.error || "Failed to update project");
    } finally {
      setEditSaving(false);
    }
  };

  const openEditModal = () => {
    editForm.setFieldsValue({
      name: project?.name,
      embedding_model: project?.embedding_model,
      llm_model: project?.llm_model,
    });
    setEditModal(true);
  };

  const handleCreateKey = async () => {
    try {
      const { data } = await createApiKey(id);
      setNewKeyVisible(data.key);
      message.success("API key created");
      fetchApiKeys();
    } catch {
      message.error("Failed to create API key");
    }
  };

  const handleCreateDoc = async (values) => {
    setDocCreating(true);
    try {
      await createDocument(id, values);
      message.success("Document created");
      setDocModal(false);
      form.resetFields();
      fetchDocuments();
    } catch (err) {
      message.error(err.response?.data?.error || "Failed to create document");
    } finally {
      setDocCreating(false);
    }
  };

  const handleDeleteDoc = async (docId) => {
    try {
      await deleteDocument(docId);
      message.success("Document deleted");
      fetchDocuments();
    } catch {
      message.error("Failed to delete document");
    }
  };

  const handleEmbed = async () => {
    if (!embedInput.trim()) {
      message.warning("Please enter some text");
      return;
    }
    setEmbedding(true);
    setEmbedResult(null);
    try {
      const { data } = await embedText(id, embedInput);
      setEmbedResult(data);
    } catch (err) {
      message.error(err.response?.data?.error || "Embedding failed");
    } finally {
      setEmbedding(false);
    }
  };

  const handleIndexJsonFile = async (file) => {
    setIndexing(true);
    try {
      const { data } = await indexJsonFile(id, file);
      message.success(data.message);
      fetchIndexStatus();
    } catch (err) {
      message.error(err.response?.data?.detail || "Indexing failed");
    } finally {
      setIndexing(false);
    }
    return false;
  };

  const handleIndexText = async () => {
    if (!idxTextInput.trim()) {
      message.warning("Please enter text to index");
      return;
    }
    setIndexing(true);
    try {
      const { data } = await indexText(id, idxTextInput);
      message.success(data.message);
      setIdxTextInput("");
      fetchIndexStatus();
    } catch (err) {
      message.error(err.response?.data?.detail || "Indexing failed");
    } finally {
      setIndexing(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      message.warning("Please enter a search query");
      return;
    }
    setSearching(true);
    setSearchResults(null);
    try {
      const { data } = await searchIndex(id, searchQuery, searchTopK);
      setSearchResults(data);
    } catch (err) {
      message.error(err.response?.data?.detail || "Search failed");
    } finally {
      setSearching(false);
    }
  };

  const handleClearIndex = async () => {
    try {
      await clearIndex(id);
      message.success("Index cleared");
      fetchIndexStatus();
      setSearchResults(null);
    } catch (err) {
      message.error(err.response?.data?.detail || "Clear failed");
    }
  };

  const handleChatSend = async () => {
    const q = chatInput.trim();
    if (!q) return;
    const userMsg = { role: "user", content: q };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput("");
    setChatLoading(true);
    try {
      const { data } = await queryRAG(id, q, { topK: chatTopK });
      const botMsg = {
        role: "assistant",
        content: data.answer,
        context: data.context,
        llm_model: data.llm_model,
        embedding_model: data.embedding_model,
      };
      setChatMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errMsg = {
        role: "assistant",
        content: `Error: ${err.response?.data?.detail || "Query failed"}`,
      };
      setChatMessages((prev) => [...prev, errMsg]);
    } finally {
      setChatLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    message.success("Copied to clipboard");
  };

  const statusColor = {
    uploaded: "blue",
    processing: "orange",
    indexed: "green",
    failed: "red",
  };

  const keyColumns = [
    { title: "ID", dataIndex: "id", key: "id", ellipsis: true },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (s) => <Tag color={s === "active" ? "green" : "default"}>{s}</Tag>,
    },
    {
      title: "Created At",
      dataIndex: "created_at",
      key: "created_at",
      render: (v) => new Date(v).toLocaleString(),
    },
  ];

  const docColumns = [
    { title: "File Name", dataIndex: "file_name", key: "file_name" },
    {
      title: "S3 Path",
      dataIndex: "s3_path",
      key: "s3_path",
      ellipsis: true,
      render: (v) => v || "—",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (s) => <Tag color={statusColor[s] || "default"}>{s}</Tag>,
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
        <Popconfirm
          title="Delete this document?"
          onConfirm={() => handleDeleteDoc(record.id)}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            Delete
          </Button>
        </Popconfirm>
      ),
    },
  ];

  if (loading.project) return null;

  const tabItems = [
    {
      key: "chat",
      label: (
        <span>
          <MessageOutlined /> RAG Chat
        </span>
      ),
      children: (
        <div style={{ maxWidth: 800 }}>
          <Paragraph type="secondary">
            Ask questions about your indexed documents. Uses
            <Tag color="purple" style={{ margin: "0 4px" }}>{project?.embedding_model}</Tag>
            for retrieval and
            <Tag color="geekblue" style={{ margin: "0 4px" }}>{project?.llm_model}</Tag>
            for generation.
          </Paragraph>
          <Space style={{ marginBottom: 16 }}>
            <Text type="secondary">Top K:</Text>
            <InputNumber min={1} max={20} value={chatTopK} onChange={setChatTopK} size="small" />
          </Space>

          <div
            style={{
              border: "1px solid #f0f0f0",
              borderRadius: 8,
              height: 420,
              overflowY: "auto",
              padding: 16,
              background: "#fafafa",
              marginBottom: 12,
              display: "flex",
              flexDirection: "column",
              gap: 12,
            }}
          >
            {chatMessages.length === 0 && (
              <div style={{ textAlign: "center", color: "#bbb", paddingTop: 160 }}>
                Ask a question to get started...
              </div>
            )}
            {chatMessages.map((msg, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                }}
              >
                <div
                  style={{
                    maxWidth: "75%",
                    padding: "10px 14px",
                    borderRadius: 12,
                    background: msg.role === "user" ? "#6366f1" : "#fff",
                    color: msg.role === "user" ? "#fff" : "#333",
                    border: msg.role === "user" ? "none" : "1px solid #e8e8e8",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
                  }}
                >
                  <div style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{msg.content}</div>
                  {msg.context && msg.context.length > 0 && (
                    <details style={{ marginTop: 8, fontSize: 12, color: "#888" }}>
                      <summary style={{ cursor: "pointer" }}>
                        {msg.context.length} source(s) · {msg.llm_model}
                      </summary>
                      <div style={{ marginTop: 4 }}>
                        {msg.context.map((c, j) => (
                          <div
                            key={j}
                            style={{
                              padding: "4px 8px",
                              margin: "4px 0",
                              background: "#f5f5f5",
                              borderRadius: 4,
                              borderLeft: "3px solid #6366f1",
                            }}
                          >
                            <strong>{c.title || "Untitled"}</strong> (score: {c.score})
                            <br />
                            <span style={{ color: "#666" }}>
                              {c.content.length > 200 ? c.content.slice(0, 200) + "..." : c.content}
                            </span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </div>
            ))}
            {chatLoading && (
              <div style={{ display: "flex", justifyContent: "flex-start" }}>
                <div
                  style={{
                    padding: "10px 14px",
                    borderRadius: 12,
                    background: "#fff",
                    border: "1px solid #e8e8e8",
                    color: "#999",
                  }}
                >
                  Thinking...
                </div>
              </div>
            )}
          </div>

          <Space.Compact style={{ width: "100%" }}>
            <Input
              placeholder="Ask a question about your documents..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onPressEnter={handleChatSend}
              disabled={chatLoading}
              prefix={<MessageOutlined />}
              size="large"
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleChatSend}
              loading={chatLoading}
              size="large"
            >
              Send
            </Button>
          </Space.Compact>
        </div>
      ),
    },
    {
      key: "keys",
      label: (
        <span>
          <KeyOutlined /> API Keys
        </span>
      ),
      children: (
        <>
          <div style={{ marginBottom: 16, display: "flex", justifyContent: "flex-end" }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateKey}>
              Generate Key
            </Button>
          </div>
          <Table
            columns={keyColumns}
            dataSource={apiKeys}
            rowKey="id"
            loading={loading.keys}
            pagination={false}
          />
        </>
      ),
    },
    {
      key: "docs",
      label: (
        <span>
          <FileTextOutlined /> Documents
        </span>
      ),
      children: (
        <>
          <div style={{ marginBottom: 16, display: "flex", justifyContent: "flex-end" }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setDocModal(true)}>
              Add Document
            </Button>
          </div>
          <Table
            columns={docColumns}
            dataSource={documents}
            rowKey="id"
            loading={loading.docs}
            pagination={false}
          />
        </>
      ),
    },
    {
      key: "indexing",
      label: (
        <span>
          <CloudUploadOutlined /> Indexing
        </span>
      ),
      children: (
        <div>
          <Space style={{ marginBottom: 16 }}>
            {idxStatus && (
              <Statistic
                title="Indexed Documents"
                value={idxStatus.document_count}
                prefix={<DatabaseOutlined />}
              />
            )}
          </Space>

          <Divider orientation="left">Upload JSON File</Divider>
          <Paragraph type="secondary">
            Upload a JSON file containing an array of objects with <code>title</code> and <code>context</code> fields.
            Documents will be tokenized (Vietnamese), vectorized using <Tag color="purple">{project?.embedding_model}</Tag>, and indexed into Weaviate.
          </Paragraph>
          <Upload
            accept=".json"
            showUploadList={false}
            beforeUpload={handleIndexJsonFile}
            disabled={indexing}
          >
            <Button icon={<UploadOutlined />} loading={indexing} type="primary">
              Upload & Index JSON
            </Button>
          </Upload>

          <Divider orientation="left">Index Single Text</Divider>
          <TextArea
            rows={3}
            placeholder="Enter text to index..."
            value={idxTextInput}
            onChange={(e) => setIdxTextInput(e.target.value)}
            style={{ marginBottom: 12, maxWidth: 600 }}
          />
          <br />
          <Button type="primary" loading={indexing} onClick={handleIndexText}>
            Index Text
          </Button>

          <Divider orientation="left">Manage Index</Divider>
          <Popconfirm title="Clear all indexed data for this project?" onConfirm={handleClearIndex}>
            <Button danger icon={<DeleteOutlined />}>
              Clear Index
            </Button>
          </Popconfirm>
        </div>
      ),
    },
    {
      key: "search",
      label: (
        <span>
          <SearchOutlined /> Search
        </span>
      ),
      children: (
        <div style={{ maxWidth: 700 }}>
          <Paragraph type="secondary">
            Search indexed documents using semantic similarity.
            Your query will be vectorized with <Tag color="purple">{project?.embedding_model}</Tag> and matched against Weaviate.
          </Paragraph>
          <Space.Compact style={{ width: "100%", marginBottom: 12 }}>
            <Input
              placeholder="Enter search query..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onPressEnter={handleSearch}
              prefix={<SearchOutlined />}
            />
            <InputNumber
              min={1}
              max={100}
              value={searchTopK}
              onChange={setSearchTopK}
              style={{ width: 100 }}
              addonBefore="Top"
            />
            <Button type="primary" loading={searching} onClick={handleSearch}>
              Search
            </Button>
          </Space.Compact>

          {searchResults && (
            <>
              <Alert
                type="info"
                showIcon
                message={`Found ${searchResults.total} result(s) using model "${searchResults.model}"`}
                style={{ marginBottom: 12 }}
              />
              <List
                dataSource={searchResults.results}
                renderItem={(item, idx) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <Tag color="blue" style={{ minWidth: 40, textAlign: "center" }}>
                          #{idx + 1}
                        </Tag>
                      }
                      title={
                        <Space>
                          {item.metadata?.title && <Text strong>{item.metadata.title}</Text>}
                          <Tag color="green">Score: {item.score}</Tag>
                        </Space>
                      }
                      description={
                        <Paragraph
                          ellipsis={{ rows: 3, expandable: true, symbol: "more" }}
                          style={{ marginBottom: 0 }}
                        >
                          {item.content}
                        </Paragraph>
                      }
                    />
                  </List.Item>
                )}
              />
            </>
          )}
        </div>
      ),
    },
    {
      key: "embed",
      label: (
        <span>
          <RobotOutlined /> Embedding Playground
        </span>
      ),
      children: (
        <div style={{ maxWidth: 700 }}>
          <Paragraph type="secondary">
            Test the embedding model configured for this project
            (<Tag color="purple">{project?.embedding_model}</Tag>).
            Enter text below and click Embed.
          </Paragraph>
          <TextArea
            rows={4}
            placeholder="Enter text to embed..."
            value={embedInput}
            onChange={(e) => setEmbedInput(e.target.value)}
            style={{ marginBottom: 12 }}
          />
          <Button type="primary" loading={embedding} onClick={handleEmbed}>
            Embed
          </Button>
          {embedResult && (
            <Card size="small" style={{ marginTop: 16 }}>
              <Descriptions column={2} size="small">
                <Descriptions.Item label="Model">
                  <Tag color="purple">{embedResult.model}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Dimension">
                  {embedResult.dimension}
                </Descriptions.Item>
              </Descriptions>
              <div style={{ marginTop: 8 }}>
                <Text strong>Vector</Text>
                <Button
                  size="small"
                  icon={<CopyOutlined />}
                  style={{ marginLeft: 8 }}
                  onClick={() => copyToClipboard(JSON.stringify(embedResult.vector))}
                >
                  Copy
                </Button>
              </div>
              <div
                style={{
                  marginTop: 8,
                  maxHeight: 160,
                  overflow: "auto",
                  background: "#f5f5f5",
                  padding: 12,
                  borderRadius: 6,
                  fontFamily: "monospace",
                  fontSize: 12,
                  wordBreak: "break-all",
                }}
              >
                [{embedResult.vector.map((v) => v.toFixed(6)).join(", ")}]
              </div>
            </Card>
          )}
        </div>
      ),
    },
  ];

  return (
    <>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate("/")}>
          Back
        </Button>
      </Space>

      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Title level={4} style={{ marginTop: 0, marginBottom: 0 }}>
            {project?.name}
          </Title>
          <Button icon={<EditOutlined />} onClick={openEditModal}>
            Edit Project
          </Button>
        </div>
        <Descriptions column={2} size="small" style={{ marginTop: 16 }}>
          <Descriptions.Item label="ID">
            <Text copyable={{ text: project?.id }}>{project?.id}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color={project?.status === "active" ? "green" : "default"}>
              {project?.status}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Embedding Model">
            <Tag icon={<RobotOutlined />} color="purple">{project?.embedding_model}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="LLM Model">
            <Tag icon={<RobotOutlined />} color="geekblue">{project?.llm_model}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Tenant ID">{project?.tenant_id}</Descriptions.Item>
          <Descriptions.Item label="Created At">
            {project?.created_at && new Date(project.created_at).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <Card>
        <Tabs items={tabItems} />
      </Card>

      <Modal
        title="New API Key"
        open={!!newKeyVisible}
        onCancel={() => setNewKeyVisible(null)}
        footer={[
          <Button key="copy" icon={<CopyOutlined />} onClick={() => copyToClipboard(newKeyVisible)}>
            Copy
          </Button>,
          <Button key="close" type="primary" onClick={() => setNewKeyVisible(null)}>
            Done
          </Button>,
        ]}
      >
        <p>Save this key now. You won't be able to see it again.</p>
        <Tooltip title="Click copy to save">
          <Input value={newKeyVisible} readOnly style={{ fontFamily: "monospace" }} />
        </Tooltip>
      </Modal>

      <Modal
        title="Add Document"
        open={docModal}
        onCancel={() => {
          setDocModal(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateDoc}>
          <Form.Item
            name="file_name"
            label="File Name"
            rules={[{ required: true, message: "Please enter file name" }]}
          >
            <Input placeholder="document.pdf" />
          </Form.Item>
          <Form.Item name="s3_path" label="S3 Path">
            <Input placeholder="s3://bucket/path/document.pdf" />
          </Form.Item>
          <Space style={{ width: "100%", justifyContent: "flex-end" }}>
            <Button onClick={() => setDocModal(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit" loading={docCreating}>
              Create
            </Button>
          </Space>
        </Form>
      </Modal>

      <Modal
        title="Edit Project"
        open={editModal}
        onCancel={() => setEditModal(false)}
        footer={null}
      >
        <Form form={editForm} layout="vertical" onFinish={handleEditProject}>
          <Form.Item
            name="name"
            label="Project Name"
            rules={[{ required: true, message: "Please enter project name" }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="embedding_model"
            label="Embedding Model"
            rules={[{ required: true, message: "Please select an embedding model" }]}
          >
            <Select
              options={models.embedding_models.map((m) => ({ value: m, label: m }))}
            />
          </Form.Item>
          <Form.Item
            name="llm_model"
            label="LLM Model"
            rules={[{ required: true, message: "Please select a LLM model" }]}
          >
            <Select
              options={models.llm_models.map((m) => ({ value: m, label: m }))}
            />
          </Form.Item>
          <Space style={{ width: "100%", justifyContent: "flex-end" }}>
            <Button onClick={() => setEditModal(false)}>Cancel</Button>
            <Button type="primary" htmlType="submit" loading={editSaving}>
              Save
            </Button>
          </Space>
        </Form>
      </Modal>
    </>
  );
}
