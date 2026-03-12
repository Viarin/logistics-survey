// src/db.ts
import Dexie from 'dexie'; // Тут ми беремо сам інструмент

// Створюємо екземпляр бази
export const db = new Dexie('SalesSurveyDB');

// Визначаємо структуру таблиць
db.version(1).stores({
  drafts: 'id' // id - це ключ (напр. 'active')
});