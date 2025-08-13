import React from 'react';

type StatCardProps = {
  title: string;
  value: React.ReactNode;
  subtitle?: string;
  color?: 'blue'|'green'|'yellow'|'purple'|'indigo'|'red'|'gray';
};

const colorMap: Record<NonNullable<StatCardProps['color']>, string> = {
  blue: 'bg-blue-500',
  green: 'bg-green-500',
  yellow: 'bg-yellow-500',
  purple: 'bg-purple-500',
  indigo: 'bg-indigo-500',
  red: 'bg-red-500',
  gray: 'bg-gray-500',
};

export default function StatCard({ title, value, subtitle, color = 'gray' }: StatCardProps) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`w-8 h-8 ${colorMap[color]} rounded-md`}></div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="text-lg font-medium text-gray-900">{value}</dd>
              {subtitle && <dd className="text-xs text-gray-500 mt-1">{subtitle}</dd>}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}