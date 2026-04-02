.PHONY: dev-frontend dev-backend install-frontend install-backend install-all

install-all:
	@echo "Installing dependencies..."
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && pip install -r requirements.txt

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && uvicorn main:app --reload

dev: dev-frontend dev-backend

build-frontend:
	cd frontend && npm run build

clean:
	rm -rf frontend/node_modules
	rm -rf backend/__pycache__
	rm -rf backend/*/__pycache__

format:
	cd frontend && npx prettier --write .
	cd backend && black .

lint:
	cd frontend && npx eslint .
	cd backend && flake8 .
