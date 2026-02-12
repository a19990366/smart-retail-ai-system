// src/components/SalesPage.jsx
import React, { useState } from 'react';
import axios from 'axios';
import { 
  Stack, Card, Title, Text, Button, FileInput, NumberInput, 
  Stepper, Group, Alert, Table, LoadingOverlay, ThemeIcon 
} from '@mantine/core';
import { 
  IconUpload, IconBrain, IconChartLine, IconCheck, IconX 
} from '@tabler/icons-react';
import { API_URL } from '../api';

export function SalesPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState(null);
  const [predictDays, setPredictDays] = useState(7);
  const [predictions, setPredictions] = useState([]);

  // Step 1: 上傳 CSV
  const handleUpload = async () => {
    if (!file) return alert("請先選擇檔案");
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(`${API_URL}/sales/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert("✅ 資料上傳成功！");
      setActiveStep(1); // 前進下一步
    } catch (err) {
      alert("上傳失敗：" + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: 訓練模型
  const handleTrain = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_URL}/sales/train`);
      alert("🎉 模型訓練完成！");
      setActiveStep(2); // 前進下一步
    } catch (err) {
      alert("訓練失敗：" + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 3: 執行預測
  const handlePredict = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/sales/predict`, { days: predictDays });
      setPredictions(res.data.results);
      setActiveStep(3); // 完成
    } catch (err) {
      alert("預測失敗：" + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Stack spacing="xl">
      {/* 步驟條 */}
      <Stepper active={activeStep} onStepClick={setActiveStep} breakpoint="sm">
        <Stepper.Step label="上傳資料" description="CSV 銷售數據" icon={<IconUpload size={18} />} />
        <Stepper.Step label="訓練模型" description="Prophet AI 運算" icon={<IconBrain size={18} />} />
        <Stepper.Step label="參數設定" description="預測天數" icon={<IconChartLine size={18} />} />
        <Stepper.Completed>
          預測結果
        </Stepper.Completed>
      </Stepper>

      {/* Step 1: 上傳區塊 */}
      {activeStep === 0 && (
        <Card withBorder shadow="sm" radius="md" p="xl">
          <Title order={4} mb="md">1. 上傳歷史銷售數據 (CSV)</Title>
          <Text c="dimmed" size="sm" mb="md">
            請上傳包含 `transaction_date` 與 `quantity` 欄位的 CSV 檔案。
          </Text>
          <Group align="flex-end">
            <FileInput 
              placeholder="選擇 CSV 檔案" 
              accept=".csv" 
              value={file} 
              onChange={setFile} 
              style={{ flex: 1 }}
            />
            <Button onClick={handleUpload} loading={loading}>上傳並寫入資料庫</Button>
          </Group>
        </Card>
      )}

      {/* Step 2: 訓練區塊 */}
      {activeStep === 1 && (
        <Card withBorder shadow="sm" radius="md" p="xl">
          <LoadingOverlay visible={loading} overlayProps={{ radius: "sm", blur: 2 }} />
          <Title order={4} mb="md">2. AI 模型訓練</Title>
          <Alert icon={<IconBrain size={16} />} title="準備就緒" color="blue" mb="md">
            資料庫已準備好，點擊按鈕開始訓練 Prophet 時間序列模型。這可能需要幾秒鐘。
          </Alert>
          <Button fullWidth size="md" color="violet" onClick={handleTrain} loading={loading}>
            開始訓練模型
          </Button>
        </Card>
      )}

      {/* Step 3: 預測設定 */}
      {activeStep === 2 && (
        <Card withBorder shadow="sm" radius="md" p="xl">
          <Title order={4} mb="md">3. 設定預測參數</Title>
          <Group align="flex-end">
            <NumberInput 
              label="預測未來幾天?" 
              value={predictDays} 
              onChange={setPredictDays} 
              min={1} max={365} 
              style={{ flex: 1 }}
            />
            <Button onClick={handlePredict} loading={loading} leftSection={<IconChartLine size={18}/>}>
              產生預測報表
            </Button>
          </Group>
        </Card>
      )}

      {/* Step 4: 結果顯示 */}
      {activeStep === 3 && (
        <Card withBorder shadow="sm" radius="md" p="xl" style={{ position: 'relative' }}>
          <Button 
            variant="subtle" size="xs" color="gray" 
            style={{ position: 'absolute', top: 10, right: 10 }}
            onClick={() => { setActiveStep(0); setPredictions([]); }}
          >
            重置流程
          </Button>
          
          <Title order={4} mb="md" c="green">🚀 未來 {predictions.length} 天銷量預測</Title>
          <Table striped highlightOnHover withTableBorder withColumnBorders>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>日期</Table.Th>
                <Table.Th>預測銷量 (件)</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {predictions.map((row) => (
                <Table.Tr key={row.date}>
                  <Table.Td>{row.date}</Table.Td>
                  <Table.Td style={{ fontWeight: 'bold', color: '#228be6' }}>
                    {row.predicted_sales}
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Card>
      )}
    </Stack>
  );
}