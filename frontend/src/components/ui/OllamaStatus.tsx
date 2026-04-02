import { useEffect, useState } from 'react';
import { Cpu, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface OllamaStatusProps {
  host?: string;
}

interface Status {
  connected: boolean;
  models: string[];
  version?: string;
  loading: boolean;
}

export function OllamaStatus({ host = 'http://localhost:11434' }: OllamaStatusProps) {
  const [status, setStatus] = useState<Status>({
    connected: false,
    models: [],
    loading: true,
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [host]);

  const checkStatus = async () => {
    setStatus((prev) => ({ ...prev, loading: true }));
    setError(null);

    try {
      // Check if Ollama is running
      const response = await fetch(`${host}/api/tags`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error('Ollama is not responding');
      }

      const data = await response.json();

      // Get version
      const versionResponse = await fetch(`${host}/api/version`);
      const versionData = versionResponse.ok ? await versionResponse.json() : {};

      setStatus({
        connected: true,
        models: data.models?.map((m: any) => m.name) || [],
        version: versionData.version,
        loading: false,
      });
    } catch (err) {
      setStatus({
        connected: false,
        models: [],
        loading: false,
      });
      setError(err instanceof Error ? err.message : 'Failed to connect');
    }
  };

  const getStatusIcon = () => {
    if (status.loading) {
      return <Loader2 className="w-5 h-5 animate-spin text-yellow-400" />;
    }
    if (status.connected) {
      return <CheckCircle className="w-5 h-5 text-green-400" />;
    }
    return <XCircle className="w-5 h-5 text-red-400" />;
  };

  const getStatusText = () => {
    if (status.loading) return 'Checking...';
    if (status.connected) {
      return `${status.models.length} model${status.models.length !== 1 ? 's' : ''} available`;
    }
    return 'Disconnected';
  };

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-[#252526] border border-[#3c3c3c] rounded-lg">
      <div className="flex items-center gap-2">
        <Cpu className="w-5 h-5 text-blue-400" />
        <span className="font-medium">Ollama</span>
      </div>

      <div className="h-4 w-px bg-[#3c3c3c]" />

      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <span className={`text-sm ${status.connected ? 'text-green-400' : 'text-red-400'}`}>
          {getStatusText()}
        </span>
      </div>

      {status.version && (
        <>
          <div className="h-4 w-px bg-[#3c3c3c]" />
          <span className="text-xs text-gray-500">v{status.version}</span>
        </>
      )}

      <button
        onClick={checkStatus}
        disabled={status.loading}
        className="ml-auto p-1.5 hover:bg-[#3c3c3c] rounded text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
        title="Refresh status"
      >
        <Loader2 className={`w-4 h-4 ${status.loading ? 'animate-spin' : ''}`} />
      </button>
    </div>
  );
}
