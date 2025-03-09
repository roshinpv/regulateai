import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import morgan from 'morgan';
import helmet from 'helmet';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { fileURLToPath } from 'url';
import path from 'path';
import { setupDatabase } from './database.js';
import logger from './utils/logger.js';

// Import routes
import authRoutes from './routes/auth.js';
import regulationsRoutes from './routes/regulations.js';
import agenciesRoutes from './routes/agencies.js';
import banksRoutes from './routes/banks.js';
import alertsRoutes from './routes/alerts.js';
import updatesRoutes from './routes/updates.js';
import graphRoutes from './routes/graph.js';
import assistantRoutes from './routes/assistant.js';

// Load environment variables
dotenv.config();

// Initialize express app
const app = express();
const PORT = process.env.PORT || 5000;

// Setup middleware
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));
app.use(helmet());
app.use(compression());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Setup database
setupDatabase()
  .then(() => {
    logger.info('Database initialized successfully');
  })
  .catch((err) => {
    logger.error('Database initialization failed:', err);
    process.exit(1);
  });

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/regulations', regulationsRoutes);
app.use('/api/agencies', agenciesRoutes);
app.use('/api/banks', banksRoutes);
app.use('/api/alerts', alertsRoutes);
app.use('/api/updates', updatesRoutes);
app.use('/api/graph', graphRoutes);
app.use('/api/assistant', assistantRoutes);

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  app.use(express.static(path.join(__dirname, '../dist')));
  
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../dist/index.html'));
  });
}

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error(err.stack);
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
});

export default app;