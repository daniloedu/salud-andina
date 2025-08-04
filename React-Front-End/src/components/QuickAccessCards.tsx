import React from 'react';
import { Card } from '@/components/ui/card';
import { Leaf, TrendingUp, FileText } from 'lucide-react';

interface QuickAccessCardsProps {
  onRemediesClick: () => void;
  onWellnessClick: () => void;
  onTipsClick: () => void;
}

const QuickAccessCards: React.FC<QuickAccessCardsProps> = ({
  onRemediesClick,
  onWellnessClick,
  onTipsClick
}) => {
  const cards = [
    {
      title: 'Remedios Naturales',
      subtitle: 'Plantas medicinales',
      icon: Leaf,
      onClick: onRemediesClick,
      color: 'bg-secondary'
    },
    {
      title: 'Mi Bienestar',
      subtitle: 'Tendencias y logros',
      icon: TrendingUp,
      onClick: onWellnessClick,
      color: 'bg-accent'
    },
    {
      title: 'Consejos del Día',
      subtitle: 'Recomendaciones',
      icon: FileText,
      onClick: onTipsClick,
      color: 'bg-muted'
    }
  ];

  return (
    <div className="grid grid-cols-1 gap-4">
      {cards.map((card, index) => {
        const IconComponent = card.icon;
        return (
          <Card
            key={index}
            className="bg-gradient-card border border-border/30 shadow-soft rounded-2xl cursor-pointer transition-all duration-300 hover:shadow-elegant hover:-translate-y-1 relative overflow-hidden group"
            onClick={card.onClick}
          >
            <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-primary opacity-5 rounded-full -mr-10 -mt-10 group-hover:opacity-10 transition-opacity"></div>
            <div className="relative p-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-primary rounded-2xl flex items-center justify-center shadow-soft group-hover:shadow-elegant transition-all">
                  <IconComponent className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="text-lg font-medium text-card-foreground mb-1">{card.title}</h4>
                  <p className="text-muted-foreground">{card.subtitle}</p>
                </div>
                <div className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};

export default QuickAccessCards;