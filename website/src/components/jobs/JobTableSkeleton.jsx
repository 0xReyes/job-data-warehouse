import React from 'react';
import { Table, Skeleton } from 'antd';

const JobTableSkeleton = ({ columns }) => {
  const skeletonData = Array.from({ length: 10 }).map((_, i) => ({
    id: `skeleton-${i}`,
    title: <Skeleton.Input style={{ width: 200 }} active size="small" />,
    company: <Skeleton.Input style={{ width: 120 }} active size="small" />,
    details: <Skeleton paragraph={{ rows: 2, width: '100%' }} active />,
    source: <Skeleton.Button active size="small" />,
    actions: <Skeleton.Button active size="small" />,
  }));

  const skeletonColumns = columns.map(col => {
      if (col.key === 'role') return { ...col, render: (_, record) => <div>{record.title}<br/>{record.company}</div> };
      if (col.key === 'details') return { ...col, render: (_, record) => record.details };
      if (col.key === 'source') return { ...col, render: (_, record) => record.source };
      if (col.key === 'actions') return { ...col, render: (_, record) => record.actions };
      return col;
  });

  return (
      <Table
          columns={skeletonColumns}
          dataSource={skeletonData}
          rowKey="id"
          pagination={false}
          className="job-table"
      />
  );
};

export default JobTableSkeleton;
