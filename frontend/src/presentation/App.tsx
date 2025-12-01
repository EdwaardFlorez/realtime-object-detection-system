import { useState } from 'react';
import { WebcamView } from './components/WebcamView';
import { Video, Upload } from 'lucide-react';

function App() {
  const [mode, setMode] = useState<'webcam' | 'upload'>('webcam');

  return (
    // Cambios clave: 'h-screen' (pantalla completa), 'overflow-hidden' (sin scrollbars)
    <div className="h-screen w-screen bg-slate-900 text-white flex flex-col overflow-hidden">
      
      {/* Header compacto */}
      <header className="h-16 shrink-0 flex items-center justify-between px-6 border-b border-slate-700 bg-slate-950">
        <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-blue-400">Sistema YOLOv11</h1>
            <span className="px-2 py-0.5 bg-slate-800 rounded text-xs text-slate-400">Tesis Ingeniería</span>
        </div>

        <div className="flex gap-2">
            <button 
                onClick={() => setMode('webcam')}
                className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded transition-colors ${mode === 'webcam' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
            >
                <Video size={16} /> En Vivo
            </button>
            <button 
                onClick={() => setMode('upload')}
                className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded transition-colors ${mode === 'upload' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
            >
                <Upload size={16} /> Archivo
            </button>
        </div>
      </header>

      {/* Main: Ocupa el resto de la altura y TODO el ancho */}
      <main className="flex-1 w-full h-full relative">
        {mode === 'webcam' ? (
            <WebcamView />
        ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
                Módulo de carga en construcción...
            </div>
        )}
      </main>
    </div>
  );
}

export default App;