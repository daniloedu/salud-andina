import React from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Heart, Sparkles } from 'lucide-react';

interface DailyCheckinProps {
  onStartCheckin: () => void;
  isCompleted: boolean;
}

const DailyCheckin: React.FC<DailyCheckinProps> = ({ onStartCheckin, isCompleted }) => {
  return (
    <Card className="bg-gradient-card border border-border/30 shadow-soft rounded-2xl overflow-hidden relative">
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-accent opacity-5 rounded-full -mr-12 -mt-12"></div>
      <div className="relative p-8">
        <div className="text-center">
          <div className="mb-6">
            <div className="w-20 h-20 mx-auto bg-gradient-accent rounded-3xl flex items-center justify-center mb-4 shadow-elegant">
              {isCompleted ? (
                <Sparkles className="w-10 h-10 text-white" />
              ) : (
                <Heart className="w-10 h-10 text-white" />
              )}
            </div>
            <h3 className="text-2xl font-light text-card-foreground mb-3 tracking-tight">
              {isCompleted ? '¡Chequeo Completo!' : 'Chequeo Diario'}
            </h3>
            <p className="text-muted-foreground leading-relaxed">
              {isCompleted 
                ? 'Ya registraste tu bienestar hoy. ¡Excelente!' 
                : 'Cuéntame cómo te sientes hoy'
              }
            </p>
          </div>
          
          <Button
            onClick={onStartCheckin}
            size="lg"
            disabled={isCompleted}
            className={`
              w-full font-medium rounded-xl py-4 transition-all duration-300 ${
                isCompleted 
                  ? 'bg-muted text-muted-foreground cursor-not-allowed' 
                  : 'bg-gradient-primary text-primary-foreground hover:shadow-elegant shadow-soft'
              }
            `}
          >
            {isCompleted ? 'Completado Hoy' : '¿Cómo te sientes?'}
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default DailyCheckin;