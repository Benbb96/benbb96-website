// Classe pour gérer le chronomètre du jeu

class Timer {
  
  constructor() {
    this.time = 0;  // On réinitialise le temps enregistré à 0
    this.restart();  // On démarre le timer
  }
  
  // Fonction pour démarrer ou redémarrer le chrono
  restart() {
    this.start = millis();  // On enregistre le temps depuis que le jeu a été lancé, pour ensuite le comparer à un autre temps et ainsi avoir la différence
    this.isRunning = true;  // Permet de s'assurer que le timer est en route ou non
  }
  
  // Mettre en pause le timer
  pause() {
    this.time += millis() - this.start; // Calcul de la durée et on l'ajoute au temps déjà enregistré
    this.isRunning = false;
  }
  
  // Quand c'est la fin du labyrinthe
  end() {
    if (this.isRunning) {
      this.pause();
      console.log(this.getDisplay());
    }
  }
  
  getDays() {
    return this.time / 1000 / 60 / 60 / 24;  // Calcul du nombre de jours
  }
  
  getHours() {
    return this.time / 1000 / 60 / 60;  // Calcul du nombre d'heures
  }
  
  getMinutes() {
    return this.time / 1000 / 60;  // Calcul du nombre de minutes
  }
  
  getSeconds() {
    return this.time / 1000;  // Calcul du nombre de seconde
  }
  
  
  getDisplay() {
    let text = "";
    if (this.getSeconds() > 1) {  // S'il y a au moins une seconde
      if (this.getMinutes() > 1) {  // S'il y a au moins une minute
        if (this.getHours() > 1) {  // S'il y a au moins une heure
          if (this.getDays() > 1) {  // S'il y a au moins un jour
            text += this.getDays() + "j ";
          }
          text += this.getHours() + "h ";
        }
        text += this.getMinutes() % 60 + "m ";
      }
      text += this.getSeconds() % 60 + "s ";
    }
    text += this.time % 1000 + "ms";
    return text;
  }
}