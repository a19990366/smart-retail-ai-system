import React, { useState } from 'react';
import MDEditor from '@uiw/react-md-editor';
import axios from 'axios';
import { 
  Stack, Paper, Group, TextInput, Select, Radio, Button, Box, Card, 
  Text, Badge, Grid, Tooltip, ActionIcon, Loader 
} from '@mantine/core';
import { 
  IconSearch, IconPencil, IconThumbUp, IconThumbDown 
} from '@tabler/icons-react';
import { API_URL } from '../api';

export function SearchPage({ categories, onEdit }) {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('smart');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setHasSearched(true);
    try {
      const res = await axios.post(`${API_URL}/search`, { 
        query, 
        top_k: 5,
        search_type: searchType,
        category_filter: categoryFilter || null
      });
      setResults(res.data.results);
    } catch (err) {
      alert("搜尋失敗");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (docId, action) => {
    try {
      await axios.post(`${API_URL}/documents/${docId}/feedback`, { action });
      setResults(prev => prev.map(doc => {
        if (doc.id === docId) {
          return {
            ...doc,
            helpful_count: action === 'helpful' ? doc.helpful_count + 1 : doc.helpful_count,
            unhelpful_count: action === 'unhelpful' ? doc.unhelpful_count + 1 : doc.unhelpful_count
          };
        }
        return doc;
      }));
    } catch (err) {
      alert("評價失敗");
    }
  };

  return (
    <Stack spacing="md">
      <Paper p="xl" radius="md" withBorder bg="gray.0">
        <Stack>
          <Group align="flex-end" grow>
             <TextInput 
              label="查詢關鍵字"
              placeholder={searchType === 'smart' ? "描述問題，例如: 掃碼點餐無法結帳" : "輸入標題關鍵字"} 
              size="md"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              rightSection={loading && <Loader size="xs" />}
            />
            <Select
              label="分類過濾"
              placeholder="全部分類"
              data={['全部', ...categories]}
              value={categoryFilter}
              onChange={setCategoryFilter}
              size="md"
              clearable
              style={{ maxWidth: 200 }}
            />
          </Group>

          <Group justify="space-between" align="center" mt="xs">
            <Radio.Group value={searchType} onChange={setSearchType} name="searchType">
              <Group mt="xs">
                <Radio value="smart" label="✨ 智能語義查詢" />
                <Radio value="exact" label="🔍 精準標題查詢" />
              </Group>
            </Radio.Group>
            <Button size="md" onClick={handleSearch} loading={loading} leftSection={<IconSearch size={18}/>}>
              開始搜尋
            </Button>
          </Group>
        </Stack>
      </Paper>

      <Box>
        {results.length > 0 ? (
          results.map((doc) => (
            <Card key={doc.id} shadow="sm" padding="lg" radius="md" withBorder mb="md">
              <Group justify="space-between" mb="xs">
                <Group>
                  <Text fw={700} size="lg" c="blue">{doc.title}</Text>
                  {searchType === 'smart' && (
                    <Badge color={doc.score > 0.4 ? "green" : "gray"} variant="outline">
                      相似度: {Math.round(doc.score * 100)}%
                    </Badge>
                  )}
                </Group>
                
                <Group>
                   <Tooltip label="編輯此文件">
                    <ActionIcon variant="light" color="blue" size="lg" onClick={() => onEdit(doc)}>
                      <IconPencil size={20} />
                    </ActionIcon>
                  </Tooltip>
                  <Badge color="pink" variant="light" size="lg">{doc.category}</Badge>
                </Group>
              </Group>
              
              <Grid gutter="xl">
                <Grid.Col span={{ base: 12, md: 4 }}>
                   <Text size="sm" c="dimmed" mb={4} fw={700}>📌 大綱預覽：</Text>
                   <Paper p="xs" bg="gray.1" radius="sm">
                     <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>{doc.outline || "無大綱"}</Text>
                   </Paper>
                   
                   <Group mt="md" spacing="xs">
                      <Button 
                        variant="subtle" size="xs" color="gray" leftSection={<IconThumbUp size={16}/>}
                        onClick={() => handleFeedback(doc.id, 'helpful')}
                      >
                        有幫助 ({doc.helpful_count})
                      </Button>
                      <Button 
                        variant="subtle" size="xs" color="gray" leftSection={<IconThumbDown size={16}/>}
                        onClick={() => handleFeedback(doc.id, 'unhelpful')}
                      >
                        沒幫助 ({doc.unhelpful_count})
                      </Button>
                   </Group>
                </Grid.Col>
                <Grid.Col span={{ base: 12, md: 8 }}>
                   <Text size="sm" c="dimmed" mb={4} fw={700}>📄 詳細內容：</Text>
                   <div data-color-mode="light" style={{ border: '1px solid #eee', padding: '10px', borderRadius: '4px', maxHeight: '300px', overflowY: 'auto' }}>
                     <MDEditor.Markdown source={doc.content} />
                   </div>
                </Grid.Col>
              </Grid>
            </Card>
          ))
        ) : (
          hasSearched && !loading && (
            <Text c="dimmed" align="center" mt="xl">找不到相關文件，請嘗試切換搜尋模式或關鍵字。</Text>
          )
        )}
      </Box>
    </Stack>
  );
}