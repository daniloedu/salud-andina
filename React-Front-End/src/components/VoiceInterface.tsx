import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Mic, MicOff } from 'lucide-react';

interface VoiceInterfaceProps {
  onVoiceStart: () => void;
  onVoiceEnd: () => void;
  isListening: boolean;
}

const VoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onVoiceStart,
  onVoiceEnd,
  isListening
}) => {
  return (
    <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50">
      <div className="flex flex-col items-center gap-4">
        {isListening && (
          <div className="flex gap-2 mb-2">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="w-1.5 bg-gradient-primary rounded-full animate-voice-wave"
                style={{
                  height: Math.random() * 24 + 12,
                  animationDelay: `${i * 0.1}s`
                }}
              />
            ))}
          </div>
        )}
        
        <div className="relative">
          <Button
            size="lg"
            onClick={isListening ? onVoiceEnd : onVoiceStart}
            className={`
              relative w-20 h-20 rounded-full shadow-glow transition-all duration-300
              ${isListening 
                ? 'bg-destructive hover:bg-destructive/90 shadow-elegant scale-110' 
                : 'bg-gradient-primary hover:shadow-elegant hover:scale-105'
              }
            `}
          >
            {isListening ? (
              <MicOff className="w-8 h-8" />
            ) : (
              <Mic className="w-8 h-8" />
            )}
          </Button>
          {!isListening && (
            <div className="absolute inset-0 bg-gradient-primary rounded-full opacity-20 animate-ping"></div>
          )}
        </div>
        
        <span className="text-lg font-medium text-muted-foreground px-6 py-2 bg-card/80 backdrop-blur-sm rounded-full border border-border/30">
          {isListening ? 'Escuchando...' : 'Toca para Hablar'}
        </span>
      </div>
    </div>
  );
};

export default VoiceInterface;