import React, { useState, useEffect } from 'react';
import MDEditor from '@uiw/react-md-editor';
import axios from 'axios';
import { 
  Stack, Alert, Card, Group, Text, Badge, Grid, TextInput, Select, 
  MultiSelect, Textarea, Button, Box 
} from '@mantine/core';
import { 
  IconPencil, IconThumbUp, IconThumbDown, IconTrash, IconDeviceFloppy 
} from '@tabler/icons-react';
import { API_URL } from '../api';

export function ManagePage({ categories, tagsList, refreshConfig, editData, onComplete }) {
  const [id, setId] = useState(null);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState(categories[0] || '');
  const [selectedTags, setSelectedTags] = useState([]);
  const [outline, setOutline] = useState('');
  const [content, setContent] = useState('');
  const [stats, setStats] = useState({ helpful: 0, unhelpful: 0 });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (editData) {
      setId(editData.id);
      setTitle(editData.title);
      setCategory(editData.category);
      setSelectedTags(editData.tags || []);
      setOutline(editData.outline);
      setContent(editData.content);
      setStats({ helpful: editData.helpful_count, unhelpful: editData.unhelpful_count });
    } else {
      resetForm();
    }
  }, [editData]);

  const resetForm = () => {
    setId(null);
    setTitle('');
    setCategory(categories[0] || '');
    setSelectedTags([]);
    setOutline('');
    setContent('');
    setStats({ helpful: 0, unhelpful: 0 });
  };

  if (!category && !id && categories.length > 0) setCategory(categories[0]);

  const onPaste = async (event) => {
    const items = event.clipboardData.items;
    for (const item of items) {
      if (item.type.indexOf("image") !== -1) {
        event.preventDefault();
        const file = item.getAsFile();
        const formData = new FormData();
        formData.append("file", file);

        try {
          const placeholder = `![上傳中...](...)`;
          setContent((prev) => prev + `\n${placeholder}`);
          const res = await axios.post(`${API_URL}/upload/image`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          const imgUrl = res.data.url; 
          setContent((prev) => prev.replace(placeholder, `![image](${API_URL}${imgUrl})`));
        } catch (err) {
          alert("圖片上傳失敗");
        }
      }
    }
  };

  const handleSubmit = async () => {
    if (!title || !content || !category) return alert("標題、分類與內容必填");
    setSubmitting(true);
    const payload = { title, category, outline, content, tags: selectedTags };

    try {
      if (id) {
        await axios.put(`${API_URL}/documents/${id}`, payload);
        alert("✅ 更新成功！");
      } else {
        await axios.post(`${API_URL}/documents/create`, payload);
        alert("✅ 新增成功！");
      }
      resetForm();
      refreshConfig();
      if (onComplete) onComplete();
    } catch (err) {
      alert("儲存失敗");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("⚠️ 確定要刪除此文件嗎？此動作無法復原！")) return;
    try {
      await axios.delete(`${API_URL}/documents/${id}`);
      alert("🗑️ 已刪除");
      resetForm();
      if (onComplete) onComplete();
    } catch (err) {
      alert("刪除失敗");
    }
  };

  return (
    <Stack spacing="lg">
      {id && (
        <Alert icon={<IconPencil size={16} />} title="編輯模式" color="blue" withCloseButton onClose={onComplete}>
          您正在編輯 ID: {id} 的文件。若要切換回新增模式，請點擊右側 X。
        </Alert>
      )}

      <Card withBorder shadow="sm" radius="md" p="md">
        <Card.Section withBorder inheritPadding py="xs" bg="gray.0">
          <Group justify="space-between">
            <Text fw={500} size="sm" c="dimmed">1. 文件基本資訊</Text>
            <Group>
               {id && (
                <Group gap="xs" mr="md">
                  <Badge color="teal" leftSection={<IconThumbUp size={12}/>}>{stats.helpful}</Badge>
                  <Badge color="red" leftSection={<IconThumbDown size={12}/>}>{stats.unhelpful}</Badge>
                </Group>
               )}
               <Badge variant="outline" color={id ? "blue" : "gray"}>
                 {id ? "Update" : "Create"}
               </Badge>
            </Group>
          </Group>
        </Card.Section>
        
        <Grid mt="md">
          <Grid.Col span={6}>
            <TextInput 
              label="文件標題" 
              placeholder="例如: 掃碼點餐出廠設置" 
              value={title} 
              onChange={(e) => setTitle(e.target.value)} 
              required
            />
          </Grid.Col>
          <Grid.Col span={6}>
            <Select 
              label="主分類" 
              data={categories} 
              value={category} 
              onChange={setCategory}
              searchable
              nothingFoundMessage="無此分類，請至配置頁新增"
            />
          </Grid.Col>
          <Grid.Col span={12}>
             <MultiSelect 
              label="標籤 (Tags)" 
              placeholder="選擇或輸入標籤" 
              data={tagsList}
              value={selectedTags} 
              onChange={setSelectedTags}
              searchable
              creatable
              getCreateLabel={(query) => `+ 新增標籤 ${query}`}
              onCreate={(query) => {
                const item = { value: query, label: query };
                return item;
              }}
            />
          </Grid.Col>
          <Grid.Col span={12}>
             <Textarea 
              label="大綱 (Outline)" 
              placeholder="簡述文件重點..." 
              autosize 
              minRows={2} 
              value={outline} 
              onChange={(e) => setOutline(e.target.value)} 
            />
          </Grid.Col>
        </Grid>
      </Card>

      <Card withBorder shadow="sm" radius="md" p="md">
        <Card.Section withBorder inheritPadding py="xs" bg="gray.0">
          <Group justify="space-between">
            <Text fw={500} size="sm" c="dimmed">2. 內容編輯</Text>
            <Group>
              {id && (
                <Button 
                  color="red" variant="light" size="xs" 
                  leftSection={<IconTrash size={14}/>} 
                  onClick={handleDelete}
                >
                  刪除文件
                </Button>
              )}
              <Button 
                size="xs" color="green" 
                leftSection={<IconDeviceFloppy size={14}/>} 
                onClick={handleSubmit} 
                loading={submitting}
              >
                {id ? "更新文件" : "儲存文件"}
              </Button>
            </Group>
          </Group>
        </Card.Section>
        <Box mt="md">
          <div data-color-mode="light">
            <MDEditor value={content} onChange={setContent} onPaste={onPaste} height={600} preview="live" />
          </div>
        </Box>
      </Card>
    </Stack>
  );
}