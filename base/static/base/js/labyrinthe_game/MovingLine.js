// La classe des lignes animées

let SIZE = 60;  // La taille de la ligne

class MovingLine {

    constructor(a, b, animations) {
        this.t = a;
        this.initialT = createVector();
        this.a = createVector(0, 0);
        this.b = b;
        this.animation = 0;  // Indique quelle est l'animation en cours
        this.animations = animations;  // La liste des animations à jouer dans l'ordre
        this.r = 0;
        this.initialR = 0;
        this.speed = 0.005;  // => 0.026
        this.index = 0;  // L'index de l'animation en cours (démarre de 0 puis est incrémenté à l'appel de getAnimation() )
        this.ready = true;
    }

    show() {
        // Lance l'animation à intervalle régulier
        if (frameCount === 30 || frameCount % (1.25 / this.speed) === 0) {
            this.setAnimation(this.getAnimation());
        }

        switch (this.animation) {

            // Rotations dans le sens horaire
            case 1 :
            case 3 :
                // Tant que la rotation n'est pas arrivée à un quart de tour, on l'incrémente
                if (this.r < this.initialR + HALF_PI) this.r += this.speed / 0.65;
                else this.endAnimation(true);
                break;

            // Rotations dans le sens anti-horaire
            case 2 :
            case 4 :
                if (this.r > this.initialR - HALF_PI) this.r -= this.speed / 0.65;
                else this.endAnimation(true);
                break;

            // Translations
            case 5 :
                if ((this.b.x + this.b.y) * (this.t.x + this.t.y) < (this.b.x + this.b.y) * ((this.initialT.x + this.initialT.y) + (this.b.x + this.b.y))) {
                    this.t.set(this.t.x + this.b.x * this.speed, this.t.y + this.b.y * this.speed);
                } else this.endAnimation(false);
                break;
            case 6 :
                if ((this.b.x + this.b.y) * (this.t.x + this.t.y) > (this.b.x + this.b.y) * ((this.initialT.x + this.initialT.y) - (this.b.x + this.b.y))) {
                    this.t.set(this.t.x - this.b.x * this.speed, this.t.y - this.b.y * this.speed);
                } else this.endAnimation(false);
                break;

            default :
                this.animation = 0;
                this.ready = true;
        }

        push();
        translate(this.t.x * SIZE, this.t.y * SIZE);  // On applique la nouvelle translation
        rotate(this.r);  // On applique la nouvelle rotation
        line(this.a.x * SIZE, this.a.y * SIZE, this.b.x * SIZE, this.b.y * SIZE);  // On dessine la ligne
        pop();
    }

    // Prépare et lance l'animation passée en paramètre
    setAnimation(n) {
        if (this.ready) {
            this.ready = false;
            this.animation = n;
            if (n === 3 || n === 4) { // Inversion des deux points
                this.t.add(this.b);
                this.a.set(-this.b.x, -this.b.y);
                this.b.set(0, 0);
            } else if (n === 5 || n === 6) {
                this.initialT.set(this.t.x, this.t.y);
            }
        }
    }

    // Restaure les paramètres comme il faut et en fonction de si c'est une rotation ou une translation
    endAnimation(rotation) {
        this.initialR = 0;
        this.initialT.set(this.t.x, this.t.y);
        this.r = 0;
        if (rotation) this.replace();
        this.animation = 0;
        this.ready = true;
    }

    // Permet de replacer les points correctement en fonction de la rotation qui a eu lieu
    replace() {
        if (this.animation === 1 || this.animation === 3) {  // Rotation horaire
            if (this.a.x === 0 && this.a.y === 0) {  // Le point de pivot est a
                this.b.set(-this.b.y, this.b.x);
            } else {  // Le point de pivot est b
                this.t.set(this.t.x - this.a.y, this.t.y + this.a.x);
                this.b.set(this.a.y, -this.a.x);
                this.a.set(0, 0);
            }
        } else {  // Rotation anti-horaire
            if (this.a.x === 0 && this.a.y === 0) {
                this.b.set(this.b.y, -this.b.x);
            } else {
                this.t.set(this.t.x + this.a.y, this.t.y - this.a.x);
                this.b.set(-this.a.y, this.a.x);
                this.a.set(0, 0);
            }
        }
    }

    // Retourne l'animation à jouer et l'incrémente par la même occasion
    getAnimation() {
        if (this.index === this.animations.length) {
            this.index = 0;  // L'index repart de 0 quand il a fait le tour de la liste
        }
        return this.animations[this.index++];
    }
}