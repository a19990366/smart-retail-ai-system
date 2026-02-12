import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Group, Title, Tabs } from '@mantine/core';
import { IconSearch, IconEdit, IconDatabase, IconSettings, IconChartBar } from '@tabler/icons-react';

// 引入拆分後的元件
import { SearchPage } from './components/SearchPage';
import { ManagePage } from './components/ManagePage';
import { ConfigPage } from './components/ConfigPage';
import { SalesPage } from './components/SalesPage';
import { API_URL } from './api';

function App() {
  const [activeTab, setActiveTab] = useState('search');
  
  // 全域狀態：分類與標籤列表 (供各頁面共用)
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  
  // [新增] 編輯狀態：用來從搜尋頁傳遞資料到管理頁
  const [editingDoc, setEditingDoc] = useState(null);

  // 載入設定資料
  const fetchConfig = async () => {
    try {
      const res = await axios.get(`${API_URL}/config/all`);
      setCategories(res.data.categories);
      setTags(res.data.tags);
    } catch (err) {
      console.error("無法載入設定", err);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, [activeTab]);

  // [新增] 當使用者點擊「編輯」時觸發
  const handleEditRequest = (doc) => {
    setEditingDoc(doc);
    setActiveTab('manage'); // 切換到管理頁
  };

  // [新增] 當管理頁面完成儲存或取消時觸發
  const handleEditComplete = () => {
    setEditingDoc(null);
    fetchConfig(); // 重新整理標籤
  };

  return (
    <Container size="xl" py="lg">
      <Group position="apart" mb="xl">
        <Group>
          <IconDatabase size={32} color="#228be6" />
          <Title order={2}>AI 智能知識庫</Title>
        </Group>
      </Group>
      
      <Tabs 
        value={activeTab} 
        onChange={setActiveTab} 
        variant="outline" 
        radius="md"
        defaultValue="search"
      >
        <Tabs.List mb="md">
          <Tabs.Tab value="search" leftSection={<IconSearch size={16} />}>
            知識庫搜尋
          </Tabs.Tab>
          <Tabs.Tab value="manage" leftSection={<IconEdit size={16} />}>
            {editingDoc ? `編輯中: ${editingDoc.title}` : "內容管理"}
          </Tabs.Tab>
          <Tabs.Tab value="config" leftSection={<IconSettings size={16} />}>
            系統配置
          </Tabs.Tab>
          <Tabs.Tab value="sales" leftSection={<IconChartBar size={16} />}>
            銷量預測
          </Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="search">
          <SearchPage 
            categories={categories} 
            onEdit={handleEditRequest} 
          />
        </Tabs.Panel>

        <Tabs.Panel value="manage">
          <ManagePage 
            categories={categories} 
            tagsList={tags} 
            refreshConfig={fetchConfig}
            editData={editingDoc}
            onComplete={handleEditComplete}
          />
        </Tabs.Panel>

        <Tabs.Panel value="config">
          <ConfigPage categories={categories} tagsList={tags} refreshConfig={fetchConfig} />
        </Tabs.Panel>

        <Tabs.Panel value="sales">
          <SalesPage />
        </Tabs.Panel>
      </Tabs>
    </Container>
  );
}

export default App;