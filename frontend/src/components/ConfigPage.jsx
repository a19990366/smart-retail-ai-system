import React, { useState } from 'react';
import axios from 'axios';
import { 
  Grid, Card, Title, Group, TextInput, Button, Stack, Text, ActionIcon, Badge 
} from '@mantine/core';
import { IconPlus, IconTrash, IconX } from '@tabler/icons-react';
import { API_URL } from '../api';

export function ConfigPage({ categories, tagsList, refreshConfig }) {
  const [newCat, setNewCat] = useState('');
  const [newTag, setNewTag] = useState('');

  const handleAddCat = async () => {
    if(!newCat) return;
    try {
      await axios.post(`${API_URL}/config/categories`, { name: newCat });
      setNewCat('');
      refreshConfig();
    } catch { alert("新增失敗"); }
  };

  const handleDeleteCat = async (name) => {
    if(!confirm(`確定刪除分類「${name}」？`)) return;
    await axios.delete(`${API_URL}/config/categories/${name}`);
    refreshConfig();
  };

  const handleAddTag = async () => {
    if(!newTag) return;
    try {
      await axios.post(`${API_URL}/config/tags`, { name: newTag });
      setNewTag('');
      refreshConfig();
    } catch { alert("新增失敗"); }
  };

  const handleDeleteTag = async (name) => {
    if(!confirm(`確定刪除標籤「${name}」？`)) return;
    await axios.delete(`${API_URL}/config/tags/${name}`);
    refreshConfig();
  };

  return (
    <Grid>
      <Grid.Col span={6}>
        <Card withBorder radius="md" p="md">
          <Title order={4} mb="md">📁 分類管理</Title>
          <Group mb="md">
            <TextInput 
              placeholder="新分類名稱" 
              value={newCat} 
              onChange={(e) => setNewCat(e.target.value)} 
              style={{ flex: 1 }}
            />
            <Button onClick={handleAddCat} leftSection={<IconPlus size={16}/>}>新增</Button>
          </Group>
          <Stack>
            {categories.map(c => (
              <Group key={c} justify="space-between" bg="gray.0" p="xs" style={{borderRadius: 8}}>
                <Text>{c}</Text>
                <ActionIcon color="red" variant="subtle" onClick={() => handleDeleteCat(c)}>
                  <IconTrash size={16}/>
                </ActionIcon>
              </Group>
            ))}
          </Stack>
        </Card>
      </Grid.Col>

      <Grid.Col span={6}>
        <Card withBorder radius="md" p="md">
          <Title order={4} mb="md">🏷️ 標籤管理</Title>
          <Group mb="md">
            <TextInput 
              placeholder="新標籤名稱" 
              value={newTag} 
              onChange={(e) => setNewTag(e.target.value)} 
              style={{ flex: 1 }}
            />
            <Button onClick={handleAddTag} leftSection={<IconPlus size={16}/>}>新增</Button>
          </Group>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {tagsList.map(t => (
              <Badge key={t} size="lg" variant="outline" rightSection={
                <ActionIcon size="xs" color="red" radius="xl" variant="transparent" onClick={() => handleDeleteTag(t)}>
                  <IconX size={10} />
                </ActionIcon>
              }>
                {t}
              </Badge>
            ))}
          </div>
        </Card>
      </Grid.Col>
    </Grid>
  );
}