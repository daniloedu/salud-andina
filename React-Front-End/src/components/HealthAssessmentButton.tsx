import React from 'react';
import { Button } from '@/components/ui/button';
import { Stethoscope, AlertTriangle } from 'lucide-react';

interface HealthAssessmentButtonProps {
  onAssessmentClick: () => void;
  urgencyLevel: 'normal' | 'elevated' | 'urgent';
}

const HealthAssessmentButton: React.FC<HealthAssessmentButtonProps> = ({
  onAssessmentClick,
  urgencyLevel
}) => {
  const getButtonStyle = () => {
    switch (urgencyLevel) {
      case 'urgent':
        return 'bg-destructive hover:bg-destructive/90 text-destructive-foreground border-destructive animate-gentle-pulse';
      case 'elevated':
        return 'bg-wellness-fair hover:bg-wellness-fair/90 text-white border-wellness-fair';
      default:
        return 'bg-primary hover:bg-primary/90 text-primary-foreground border-primary';
    }
  };

  const getButtonText = () => {
    switch (urgencyLevel) {
      case 'urgent':
        return 'Evaluación Urgente';
      case 'elevated':
        return 'Necesito Ayuda Médica';
      default:
        return 'Evaluación de Salud';
    }
  };

  return (
    <div className="fixed top-6 right-6 z-40">
      <Button
        onClick={onAssessmentClick}
        className={`
          flex items-center gap-3 shadow-elegant rounded-xl px-6 py-3 backdrop-blur-sm border border-border/30 transition-all duration-300 hover:shadow-glow hover:-translate-y-1
          ${getButtonStyle()}
        `}
        size="lg"
      >
        <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
          {urgencyLevel === 'urgent' ? (
            <AlertTriangle className="w-5 h-5" />
          ) : (
            <Stethoscope className="w-5 h-5" />
          )}
        </div>
        <span className="font-medium">{getButtonText()}</span>
      </Button>
    </div>
  );
};

export default HealthAssessmentButton;