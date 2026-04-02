import { useEffect, useState } from 'react';
import {
  BarChart3,
  Clock,
  GitBranch,
  MessageSquare,
  FileCode,
  Activity,
  Zap,
  TrendingUp,
} from 'lucide-react';
import { useDashboard } from '../../hooks/useDashboard';

interface DashboardStats {
  totalSessions: number;
  totalMessages: number;
  totalFiles: number;
  activeTime: string;
  gitCommits: number;
  codeLines: number;
}

interface RecentActivity {
  id: string;
  type: 'chat' | 'file' | 'git' | 'session';
  description: string;
  timestamp: Date;
}

export function Dashboard() {
  const { stats, activities, loading, refresh } = useDashboard();
  const [timeRange, setTimeRange] = useState<'day' | 'week' | 'month'>('week');

  const StatCard = ({
    icon: Icon,
    label,
    value,
    trend,
    color,
  }: {
    icon: React.ElementType;
    label: string;
    value: string | number;
    trend?: string;
    color: string;
  }) => (
    <div className="bg-[#252526] p-6 rounded-lg border border-[#3c3c3c]">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400 mb-1">{label}</p>
          <p className="text-2xl font-bold">{value}</p>
          {trend && (
            <p className="text-xs text-green-400 mt-1 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              {trend}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );

  const getActivityIcon = (type: RecentActivity['type']) => {
    switch (type) {
      case 'chat':
        return MessageSquare;
      case 'file':
        return FileCode;
      case 'git':
        return GitBranch;
      case 'session':
        return Activity;
      default:
        return Activity;
    }
  };

  const getActivityColor = (type: RecentActivity['type']) => {
    switch (type) {
      case 'chat':
        return 'text-blue-400 bg-blue-400/10';
      case 'file':
        return 'text-green-400 bg-green-400/10';
      case 'git':
        return 'text-purple-400 bg-purple-400/10';
      case 'session':
        return 'text-yellow-400 bg-yellow-400/10';
      default:
        return 'text-gray-400 bg-gray-400/10';
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - new Date(date).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return new Date(date).toLocaleDateString();
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">
            Overview of your Llama IDE activity
          </p>
        </div>
        <div className="flex items-center gap-2">
          {(['day', 'week', 'month'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1.5 rounded-lg text-sm capitalize transition-colors ${
                timeRange === range
                  ? 'bg-blue-600 text-white'
                  : 'bg-[#2d2d2d] text-gray-400 hover:text-white'
              }`}
            >
              {range}
            </button>
          ))}
          <button
            onClick={refresh}
            className="p-2 hover:bg-[#3c3c3c] rounded-lg text-gray-400 hover:text-white transition-colors"
          >
            <Activity className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="bg-[#252526] p-6 rounded-lg border border-[#3c3c3c] animate-pulse"
            >
              <div className="h-8 bg-[#3c3c3c] rounded w-1/3 mb-4" />
              <div className="h-6 bg-[#3c3c3c] rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          <StatCard
            icon={Activity}
            label="Total Sessions"
            value={stats?.totalSessions || 0}
            trend="+12% vs last {timeRange}"
            color="bg-blue-500/20 text-blue-400"
          />
          <StatCard
            icon={MessageSquare}
            label="Chat Messages"
            value={stats?.totalMessages || 0}
            trend="+8% vs last {timeRange}"
            color="bg-green-500/20 text-green-400"
          />
          <StatCard
            icon={FileCode}
            label="Files Edited"
            value={stats?.totalFiles || 0}
            color="bg-purple-500/20 text-purple-400"
          />
          <StatCard
            icon={Clock}
            label="Active Time"
            value={stats?.activeTime || '0h'}
            trend="+2h vs last {timeRange}"
            color="bg-yellow-500/20 text-yellow-400"
          />
          <StatCard
            icon={GitBranch}
            label="Git Commits"
            value={stats?.gitCommits || 0}
            color="bg-orange-500/20 text-orange-400"
          />
          <StatCard
            icon={Zap}
            label="Lines of Code"
            value={(stats?.codeLines || 0).toLocaleString()}
            color="bg-pink-500/20 text-pink-400"
          />
        </div>
      )}

      {/* Recent Activity */}
      <div className="bg-[#252526] rounded-lg border border-[#3c3c3c] overflow-hidden">
        <div className="px-6 py-4 border-b border-[#3c3c3c] flex items-center justify-between">
          <h2 className="font-semibold flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            Recent Activity
          </h2>
          <button className="text-sm text-blue-400 hover:text-blue-300">
            View All
          </button>
        </div>

        <div className="divide-y divide-[#3c3c3c]">
          {loading ? (
            [...Array(5)].map((_, i) => (
              <div key={i} className="px-6 py-4 flex items-center gap-4 animate-pulse">
                <div className="w-10 h-10 rounded-lg bg-[#3c3c3c]" />
                <div className="flex-1">
                  <div className="h-4 bg-[#3c3c3c] rounded w-1/3 mb-2" />
                  <div className="h-3 bg-[#3c3c3c] rounded w-1/4" />
                </div>
              </div>
            ))
          ) : activities.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-500">
              <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No recent activity</p>
              <p className="text-sm mt-1">Start working to see your activity here</p>
            </div>
          ) : (
            activities.map((activity: RecentActivity) => {
              const Icon = getActivityIcon(activity.type);
              return (
                <div
                  key={activity.id}
                  className="px-6 py-4 flex items-center gap-4 hover:bg-[#2d2d2d] transition-colors"
                >
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center ${getActivityColor(
                      activity.type
                    )}`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{activity.description}</p>
                    <p className="text-sm text-gray-500">
                      {formatTime(activity.timestamp)}
                    </p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
