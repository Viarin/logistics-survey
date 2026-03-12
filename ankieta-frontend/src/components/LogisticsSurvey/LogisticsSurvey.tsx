import { useEffect} from 'react';
import { useState } from 'react';
import { Model } from 'survey-core';
import { Survey } from 'survey-react-ui';
import { PlainDark } from "survey-core/themes"
// import { customTheme } from './theme';
import { db } from '../../db/db';

interface Props {
  schema: any;
}

const LogisticsSurvey = ({ schema }: Props) => {
  const [model, setModel] = useState<Model | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const saveLocally = async () => {
    if (!model) return;
    setIsSaving(true);
    try {
      await db.table('drafts').put({ id: 'active', data: model.data });
      setTimeout(() => setIsSaving(false), 500); 
    } catch (e) {
      console.error(e);
      setIsSaving(false);
    }
  };

  useEffect(() => {
    const survey = new Model(schema);
    survey.applyTheme(PlainDark);


    survey.showPageNumbers = false; 
    survey.showProgressBar = false;
    survey.progressBarType = 'pages';

    db.table('drafts').get('active').then(saved => {
      if (saved) survey.data = saved.data;
    });

    survey.onValueChanged.add((sender) => {
      db.table('drafts').put({ id: 'active', data: sender.data });
    });

    survey.onComplete.add(async (sender) => {
      await fetch('http://localhost:8000/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sender.data)
      });
      await db.table('drafts').delete('active');
    });

    setModel(survey);
  }, [schema]);

  if (!model) return null;

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Button Save Local */}
      <button
        onClick={saveLocally}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 1000,
          padding: '12px 24px',
          backgroundColor: isSaving ? '#444' : '#2ecc71',
          color: 'white',
          border: 'none',
          borderRadius: '25px',
          cursor: 'pointer',
          fontWeight: 'bold',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
        }}
      >
        {isSaving ? 'Saving...' : '💾 Save local'}
      </button>

      <Survey model={model} />
    </div>
  );
};

export default LogisticsSurvey;