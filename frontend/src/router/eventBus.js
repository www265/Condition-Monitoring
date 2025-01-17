// src/router/eventBus.js
import mitt from 'mitt';

// 使用 mitt 创建事件总线
export const EventBus = mitt();