import React, { useState, useEffect } from 'react';
import { getEvaluations } from '../services/api';
import type { EvaluationInfo } from '../types';

const EvaluationPanel: React.FC = () => {
  const [evaluations, setEvaluations] = useState<EvaluationInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvaluations();
  }, []);

  const loadEvaluations = async () => {
    try {
      const data = await getEvaluations();
      setEvaluations(data.evaluations);
    } catch (error) {
      console.error('Error loading evaluations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading evaluations...</div>;
  }

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-xl font-bold">Evaluations</h2>
      {evaluations.length === 0 ? (
        <p className="text-textSecondary">No evaluations yet</p>
      ) : (
        <div className="space-y-3">
          {evaluations.map((eval) => (
            <div key={eval.id} className="p-3 border border-border rounded-lg">
              <div className="text-sm font-medium mb-1">{eval.query}</div>
              <div className="text-xs text-textSecondary">
                Rating: {eval.rating || 'N/A'} | Chunks: {eval.num_chunks}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EvaluationPanel;
