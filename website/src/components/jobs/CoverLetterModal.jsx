import React, { useEffect } from 'react';
import { Modal, Form, Button, Typography, Input } from 'antd';

const { Title, Text } = Typography;
const { TextArea } = Input;

const CoverLetterModal = ({ visible, onClose, job, onSave, initialData }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      initialData ? form.setFieldsValue(initialData) : form.resetFields();
    }
  }, [visible, initialData, form]);

  const handleSave = () => {
    form.validateFields()
      .then(values => {
        onSave(job.id, values);
        onClose();
        message.success('Application notes saved!');
      })
      .catch(error => console.error('Form validation failed:', error));
  };

  return (
    <Modal
      title={
        <Title level={4} style={{ margin: 0, fontWeight: 500 }}>
          Notes for {job?.title}
          <Text type="secondary" style={{ display: 'block', fontWeight: 400 }}> at {job?.company}</Text>
        </Title>
      }
      open={visible}
      onCancel={onClose}
      destroyOnClose
      maskClosable={true}
      footer={[
        <Button key="back" onClick={onClose}>
          Cancel
        </Button>,
        <Button key="submit" type="primary" onClick={handleSave}>
          Save Notes
        </Button>,
      ]}
      width={700}
    >
      <Form form={form} layout="vertical" style={{ marginTop: 24 }}>
        <Form.Item name="coverLetter" label="Cover Letter Snippets & Keywords">
          <TextArea rows={6} placeholder="e.g., 'Highlight my experience with TypeScript and distributed systems...'" />
        </Form.Item>
        <Form.Item name="notes" label="General Notes">
          <TextArea rows={3} placeholder="e.g., Salary expectations, follow-up dates, recruiter contact..." />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CoverLetterModal;
