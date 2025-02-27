document.getElementById("inputForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Sayfa yenilemeyi engelle

    const mood = document.getElementById("mood").value.trim();
    const recommendations = document.getElementById("recommendations");

    if (mood === "") {
        alert("Please describe your mood.");
        return;
    }

    // Önceki filmleri temizle
    recommendations.innerHTML = "";

    // Filmleri oluştur
    const movies = ["Movie 1", "Movie 2", "Movie 3", "Movie 4"];
    movies.forEach((movie, index) => {
        let movieDiv = document.createElement("div");
        movieDiv.classList.add("movie");

        let movieImage = document.createElement("div");
        movieImage.classList.add("movie-image");

        let movieName = document.createElement("p");
        movieName.classList.add("movie-name");
        movieName.textContent = movie;

        movieDiv.appendChild(movieImage);
        movieDiv.appendChild(movieName);
        recommendations.appendChild(movieDiv);

        // Yukarıdan aşağı animasyon
        setTimeout(() => {
            movieDiv.style.opacity = "1";
            movieDiv.style.transform = "translateY(0)";
        }, index * 300); // Gecikmeli şekilde görünmesi için
    });

    recommendations.style.display = "flex";
});
