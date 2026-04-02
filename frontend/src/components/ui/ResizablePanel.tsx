import { useState, useRef, useCallback, useEffect } from 'react';
import { GripVertical } from 'lucide-react';

interface ResizablePanelProps {
  direction: 'horizontal' | 'vertical';
  defaultSize?: number; // percentage
  minSize?: number; // percentage
  maxSize?: number; // percentage
  children: [React.ReactNode, React.ReactNode];
  className?: string;
}

export function ResizablePanel({
  direction,
  defaultSize = 50,
  minSize = 20,
  maxSize = 80,
  children,
  className = '',
}: ResizablePanelProps) {
  const [size, setSize] = useState(defaultSize);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback(() => {
    setIsDragging(true);
    document.body.style.cursor = direction === 'horizontal' ? 'col-resize' : 'row-resize';
    document.body.style.userSelect = 'none';
  }, [direction]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, []);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      let newSize: number;

      if (direction === 'horizontal') {
        newSize = ((e.clientX - rect.left) / rect.width) * 100;
      } else {
        newSize = ((e.clientY - rect.top) / rect.height) * 100;
      }

      // Clamp size
      newSize = Math.max(minSize, Math.min(maxSize, newSize));
      setSize(newSize);
    },
    [isDragging, direction, minSize, maxSize]
  );

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  const [firstChild, secondChild] = children;

  const containerClass = direction === 'horizontal' ? 'flex-row' : 'flex-col';
  const firstPanelStyle =
    direction === 'horizontal' ? { width: `${size}%` } : { height: `${size}%` };
  const secondPanelStyle =
    direction === 'horizontal'
      ? { width: `${100 - size}%` }
      : { height: `${100 - size}%` };
  const dividerClass =
    direction === 'horizontal'
      ? 'w-1 cursor-col-resize flex-col'
      : 'h-1 cursor-row-resize flex-row';

  return (
    <div ref={containerRef} className={`flex ${containerClass} ${className}`}>
      {/* First panel */}
      <div
        className="overflow-hidden"
        style={firstPanelStyle}
      >
        {firstChild}
      </div>

      {/* Divider */}
      <div
        className={`flex items-center justify-center bg-[#2d2d2d] hover:bg-blue-500/50 transition-colors ${dividerClass} ${
          isDragging ? 'bg-blue-500' : ''
        }`}
        onMouseDown={handleMouseDown}
      >
        <div className={direction === 'horizontal' ? 'h-8' : 'w-8'}>
          <GripVertical
            className={`w-4 h-4 text-gray-500 ${
              direction === 'vertical' ? 'rotate-90' : ''
            }`}
          />
        </div>
      </div>

      {/* Second panel */}
      <div
        className="overflow-hidden flex-1"
        style={secondPanelStyle}
      >
        {secondChild}
      </div>
    </div>
  );
}
