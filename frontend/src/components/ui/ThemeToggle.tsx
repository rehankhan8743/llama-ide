import { Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  const themes = [
    { id: 'light', icon: Sun, label: 'Light' },
    { id: 'dark', icon: Moon, label: 'Dark' },
    { id: 'system', icon: Monitor, label: 'System' },
  ] as const;

  return (
    <div className="flex items-center gap-1 p-1 bg-[#2d2d2d] rounded-lg">
      {themes.map(({ id, icon: Icon, label }) => (
        <button
          key={id}
          onClick={() => setTheme(id as 'light' | 'dark' | 'system')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-all ${
            theme === id
              ? 'bg-[#3c3c3c] text-white'
              : 'text-gray-400 hover:text-white hover:bg-[#3c3c3c]/50'
          }`}
          title={`${label} theme`}
        >
          <Icon className="w-4 h-4" />
          <span className="hidden sm:inline">{label}</span>
        </button>
      ))}
    </div>
  );
}
