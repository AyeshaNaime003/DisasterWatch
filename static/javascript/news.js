document.addEventListener("DOMContentLoaded", function() {
    // Function to fetch disaster-related news
    function fetchDisasterNews() {
        const apiKey = 'pub_4247484e68d5e15c897c668c0414a291ea88a'; // Replace 'YOUR_API_KEY' with your actual API key from newsdata.io
        const url = `https://newsdata.io/api/1/news?apikey=pub_4247484e68d5e15c897c668c0414a291ea88a&qInTitle=earthquake OR flood OR disaster&country=pk&language=en`;
        // console.log("NEWS FETCHED")
        fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data && data.results && data.results.length > 0) {
                const newsCarouselInner = document.getElementById('news-carousel-inner');
                newsCarouselInner.innerHTML = ''; // Clear existing content

                const articles = data.results;

                for (let i = 0; i < articles.length; i += 3) {
                    const carouselItem = document.createElement('div');
                    carouselItem.classList.add('carousel-item');
                    if (i === 0) {
                        carouselItem.classList.add('active'); // Add 'active' class for the first item
                    }

                    const articleSet = articles.slice(i, i + 3); // Get three articles

                    const row = document.createElement('div');
                    row.classList.add('row');

                    articleSet.forEach(article => {
                        const col = document.createElement('div');
                        col.classList.add('col-md-4'); // Bootstrap 4 column size for 3 columns in a row

                        const articleCard = document.createElement('div');
                        articleCard.classList.add('card', 'mb-3');

                        const cardBody = document.createElement('div');
                        cardBody.classList.add('card-body', 'd-flex', 'flex-column');

                        const title = document.createElement('h5');
                        title.classList.add('card-title');
                        title.textContent = article.title;
                        title.style.fontSize = 'large';

                        const description = document.createElement('p');
                        description.classList.add('card-text');
                        description.textContent = article.description || '';
                        description.style.overflow = 'hidden';
                        description.style.textOverflow = 'ellipsis';
                        description.style.fontSize = 'small';

                        const source = document.createElement('a');
                        source.href = article.source_url;
                        source.classList.add('btn', 'readMore', 'mt-auto');
                        source.style.width = 'max-content';
                        source.style.height = 'max-content'
                        source.style.alignSelf = 'center'
                        source.style.fontSize = 'small'
                        source.textContent = 'Read More';

                        cardBody.appendChild(title);
                        cardBody.appendChild(description);
                        cardBody.appendChild(source);

                        articleCard.appendChild(cardBody);
                        col.appendChild(articleCard);
                        row.appendChild(col);
                    });

                    carouselItem.appendChild(row);
                    newsCarouselInner.appendChild(carouselItem);
                }
            } else {
                const newsCarouselInner = document.getElementById('news-carousel-inner');
                newsCarouselInner.innerHTML = '<div class="carousel-item active"><div class="card"><div class="card-body"><h5 class="card-title">No articles found</h5></div></div></div>';
            }
        })
        .catch(error => {
            console.error('Error fetching news:', error);
            const newsCarouselInner = document.getElementById('news-carousel-inner');
            newsCarouselInner.innerHTML = `<div class="carousel-item active"><div class="card"><div class="card-body"><h5 class="card-title">Error fetching news: ${error.message}</h5></div></div></div>`;
        });
    }

    // Call the function to fetch disaster news
    fetchDisasterNews();
});
