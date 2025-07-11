// security.js
import helmet from 'helmet';
import cors from 'cors';

export function setupSecurity(app) {
    app.use(helmet());
    app.use(cors({
        origin: ['https://mobilemonero.com'],
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        allowedHeaders: ['Content-Type', 'Authorization']
    }));
}
