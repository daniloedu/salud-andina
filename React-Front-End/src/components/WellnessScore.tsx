import React from 'react';
import { Card } from '@/components/ui/card';

interface WellnessScoreProps {
  score: number;
  trend: 'up' | 'down' | 'stable';
  streak: number;
}

const WellnessScore: React.FC<WellnessScoreProps> = ({ score, trend, streak }) => {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-wellness-excellent';
    if (score >= 75) return 'text-wellness-good';
    if (score >= 60) return 'text-wellness-fair';
    if (score >= 40) return 'text-wellness-poor';
    return 'text-wellness-critical';
  };

  const getScoreMessage = (score: number) => {
    if (score >= 90) return '¡Excelente bienestar!';
    if (score >= 75) return 'Buen estado de salud';
    if (score >= 60) return 'Bienestar regular';
    if (score >= 40) return 'Necesitas cuidarte más';
    return 'Requiere atención';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      default: return '→';
    }
  };

  return (
    <Card className="bg-gradient-primary border-none shadow-elegant rounded-2xl overflow-hidden relative">
      <div className="absolute top-0 left-0 w-32 h-32 bg-white/10 rounded-full -ml-16 -mt-16"></div>
      <div className="relative p-8">
        <div className="text-center mb-6">
          <div className="mb-3">
            <span className="text-sm text-primary-foreground/70 font-medium tracking-wide uppercase">Tu Bienestar Hoy</span>
          </div>
          <div className="text-5xl font-light text-primary-foreground mb-3 tracking-tight">
            {score}
            <span className="text-xl font-normal">/100</span>
          </div>
          <p className="text-primary-foreground/90 text-lg font-light">{getScoreMessage(score)}</p>
        </div>
      
        {/* Three Elegant Columns */}
        <div className="grid grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto bg-white/20 rounded-2xl flex items-center justify-center mb-3 shadow-soft">
              <span className="text-2xl">{getTrendIcon(trend)}</span>
            </div>
            <span className="text-sm text-primary-foreground/80 font-medium">Tendencia</span>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 mx-auto bg-white/20 rounded-2xl flex items-center justify-center mb-3 shadow-soft">
              <span className="text-2xl">🔥</span>
            </div>
            <div className="text-sm text-primary-foreground/80 font-medium">{streak} Días</div>
            <div className="text-xs text-primary-foreground/60">Seguidos</div>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 mx-auto bg-white/20 rounded-2xl flex items-center justify-center mb-3 shadow-soft">
              <span className="text-2xl">💚</span>
            </div>
            <div className="text-sm text-primary-foreground/80 font-medium">Estado de</div>
            <div className="text-xs text-primary-foreground/60">Salud</div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default WellnessScore;