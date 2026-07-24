# Build stage
FROM node:21-alpine AS build

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install global expo-cli (required for builds)
RUN npm install -g expo-cli

# Install dependencies (postinstall script now finds the file)
RUN npm install

# Build the web version
RUN npx expo export -p web

# Serve stage
FROM node:21-alpine AS serve

# Copy build files from previous stage
WORKDIR /app
COPY --from=build /app/dist /app

# Expose port 3000
EXPOSE 3000

# Run `serve` to serve the static files
CMD ["npx", "serve", "-s", "/app", "-l", "3000"]