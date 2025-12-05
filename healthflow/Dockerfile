# --- Étape 1 : Build (Compilation) ---
# On utilise une image avec Maven et Java 21
FROM maven:3.9.6-eclipse-temurin-21 AS build
WORKDIR /app

# 1. Copier le fichier de dépendances
COPY pom.xml .
# 2. Télécharger les libs (mise en cache pour aller plus vite les prochaines fois)
RUN mvn dependency:go-offline

# 3. Copier le code source
COPY src ./src

# 4. Compiler le projet (crée le .jar dans target/)
RUN mvn clean package -DskipTests

# --- Étape 2 : Run (Exécution légère) ---
# On repart d'une image vide juste avec Java (pas de Maven)
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# 5. On récupère UNIQUEMENT le .jar généré à l'étape 1
COPY --from=build /app/target/*.jar app.jar

# 6. Config du port et lancement
EXPOSE 8081
# On utilise la variable PORT fournie par Railway, sinon 8081 par défaut
ENTRYPOINT ["java", "-Xmx256m", "-jar", "-Dserver.port=${PORT:8081}", "app.jar"]
