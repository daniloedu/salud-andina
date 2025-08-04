import React, { useState } from 'react';
import WellnessScore from '@/components/WellnessScore';
import VoiceInterface from '@/components/VoiceInterface';
import DailyCheckin from '@/components/DailyCheckin';
import QuickAccessCards from '@/components/QuickAccessCards';
import HealthAssessmentButton from '@/components/HealthAssessmentButton';
import healingPlantsHero from '@/assets/healing-plants-hero.jpg';
import { useToast } from '@/hooks/use-toast';

const Index = () => {
  const [isListening, setIsListening] = useState(false);
  const [checkinCompleted, setCheckinCompleted] = useState(false);
  const [wellnessScore] = useState(82);
  const [wellnessTrend] = useState<'up' | 'down' | 'stable'>('up');
  const [streak] = useState(7);
  const { toast } = useToast();

  const handleVoiceStart = () => {
    setIsListening(true);
    toast({
      title: "Escuchando...",
      description: "Cuéntame cómo te sientes hoy",
    });
  };

  const handleVoiceEnd = () => {
    setIsListening(false);
    toast({
      title: "Procesando...",
      description: "Analizando tu mensaje",
    });
  };

  const handleStartCheckin = () => {
    toast({
      title: "Iniciando chequeo diario",
      description: "¿Cómo te sientes hoy?",
    });
    setCheckinCompleted(true);
  };

  const handleRemediesClick = () => {
    toast({
      title: "Remedios Naturales",
      description: "Próximamente: biblioteca de plantas medicinales",
    });
  };

  const handleWellnessClick = () => {
    toast({
      title: "Mi Bienestar",
      description: "Próximamente: tendencias y análisis detallado",
    });
  };

  const handleTipsClick = () => {
    toast({
      title: "Consejos del Día",
      description: "Próximamente: recomendaciones personalizadas",
    });
  };

  const handleAssessmentClick = () => {
    toast({
      title: "Evaluación de Salud",
      description: "Próximamente: evaluación médica guiada",
    });
  };

  const getCurrentGreeting = () => {
    const hour = new Date().getHours();
    const userName = "María"; // This would come from user data
    
    if (hour < 12) {
      return `¡Buenos días, ${userName}!`;
    } else if (hour < 18) {
      return `¡Buenas tardes, ${userName}!`;
    } else {
      return `¡Buenas noches, ${userName}!`;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-surface">
      {/* Elegant Header */}
      <div className="bg-gradient-card border-b border-border/30 backdrop-blur-sm">
        <div className="max-w-md mx-auto px-8 py-12 text-center">
          <div className="mb-4">
            <div className="w-16 h-16 mx-auto bg-gradient-primary rounded-full flex items-center justify-center mb-6 shadow-elegant">
              <svg className="w-8 h-8 text-primary-foreground" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <h1 className="text-4xl font-light text-card-foreground mb-3 tracking-tight">
              {getCurrentGreeting()}
            </h1>
            <p className="text-muted-foreground text-lg font-light">
              Cuidamos tu salud con sabiduría tradicional
            </p>
          </div>
        </div>
      </div>

      {/* Health Assessment Button */}
      <HealthAssessmentButton 
        onAssessmentClick={handleAssessmentClick}
        urgencyLevel="normal"
      />

      {/* Main Content */}
      <div className="max-w-md mx-auto px-6 py-8 space-y-8 pb-32">
        {/* Wellness Score */}
        <div className="animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <WellnessScore 
            score={wellnessScore}
            trend={wellnessTrend}
            streak={streak}
          />
        </div>

        {/* Daily Check-in */}
        <div className="animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
          <DailyCheckin 
            onStartCheckin={handleStartCheckin}
            isCompleted={checkinCompleted}
          />
        </div>

        {/* Quick Access Cards */}
        <div className="animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
          <QuickAccessCards 
            onRemediesClick={handleRemediesClick}
            onWellnessClick={handleWellnessClick}
            onTipsClick={handleTipsClick}
          />
        </div>

        {/* Daily Tip - Enhanced */}
        <div className="animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
          <div className="bg-gradient-card rounded-2xl p-6 shadow-soft border border-border/30 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-primary opacity-5 rounded-full -mr-12 -mt-12"></div>
            <div className="relative">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center shadow-soft">
                  <svg className="w-5 h-5 text-primary-foreground" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-card-foreground">
                  Consejo del Día
                </h3>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                La manzanilla en té caliente ayuda a relajar el estómago y mejorar el sueño. 
                Tómala 30 minutos antes de dormir para mejores resultados.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Voice Interface */}
      <VoiceInterface 
        onVoiceStart={handleVoiceStart}
        onVoiceEnd={handleVoiceEnd}
        isListening={isListening}
      />
    </div>
  );
};

export default Index;
