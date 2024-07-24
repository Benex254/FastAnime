"""
This module contains all the preset queries for the sake of neatness and convinience
Mostly for internal usage
"""

optional_variables = "\
$page:Int,\
$sort:[MediaSort],\
$id_in:[Int],\
$genre_in:[String],\
$genre_not_in:[String],\
$tag_in:[String],\
$tag_not_in:[String],\
$status_in:[MediaStatus],\
$status:MediaStatus,\
$status_not_in:[MediaStatus],\
$popularity_greater:Int,\
$popularity_lesser:Int,\
$averageScore_greater:Int,\
$averageScore_lesser:Int,\
$startDate_greater:FuzzyDateInt,\
$startDate_lesser:FuzzyDateInt,\
$endDate_greater:FuzzyDateInt,\
$endDate_lesser:FuzzyDateInt\
"
# FuzzyDateInt = (yyyymmdd)
# MediaStatus = (FINISHED,RELEASING,NOT_YET_RELEASED,CANCELLED,HIATUS)
search_query = (
    """
query($query:String,%s){
  Page(perPage:30,page:$page){
    pageInfo{
      total
      currentPage
      hasNextPage
    }
    media(
      search:$query,
      id_in:$id_in,
      genre_in:$genre_in,
      genre_not_in:$genre_not_in,
      tag_in:$tag_in,
      tag_not_in:$tag_not_in,
      status_in:$status_in,
      status:$status,
      status_not_in:$status_not_in,
      popularity_greater:$popularity_greater,
      popularity_lesser:$popularity_lesser,
      averageScore_greater:$averageScore_greater,
      averageScore_lesser:$averageScore_lesser,
      startDate_greater:$startDate_greater,
      startDate_lesser:$startDate_lesser,
      endDate_greater:$endDate_greater,
      endDate_lesser:$endDate_lesser,
      sort:$sort,
      type:ANIME
      )
    {
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
        large
      }
      trailer {
        site
        id
        
      }
      popularity
      favourites
      averageScore
      episodes
      genres
      studios{
        nodes{
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      description
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""
    % optional_variables
)

trending_query = """
query{  
  Page(perPage:15){
    
    media(sort:TRENDING_DESC,type:ANIME,genre_not_in:["hentai"]){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
        large
      }
      trailer {
        site
        id
      }
      popularity
      favourites
      averageScore
      genres
      episodes
      description
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name              
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

# mosts
most_favourite_query = """
query{
  Page(perPage:15){    
    media(sort:FAVOURITES_DESC,type:ANIME,genre_not_in:["hentai"]){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
        large
      }
      trailer {
        site
        id
        
      }
      popularity
      favourites
      averageScore
      episodes
      description
      genres
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name              
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

most_scored_query = """
query{
  Page(perPage:15){
    media(sort:SCORE_DESC,type:ANIME,genre_not_in:["hentai"]){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
        large
      }
      trailer {
        site
        id
        
      }
      popularity
      episodes
      favourites
      averageScore
      description
      genres
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name              
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

most_popular_query = """
query{  
  Page(perPage:15){
    media(sort:POPULARITY_DESC,type:ANIME,genre_not_in:["hentai"]){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
        large
      }
      trailer {
        site
        id
        
      }
      popularity
      favourites
      averageScore
      description
      episodes
      genres
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name              
      }      
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }  
    }
  }
}
"""

most_recently_updated_query = """
query{
  Page(perPage:15){
    media(sort:UPDATED_AT_DESC,type:ANIME,averageScore_greater:50,genre_not_in:["hentai"],status:RELEASING){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
        large
      }
      trailer {
        site
        id     
      }
      popularity
      favourites
      averageScore
      description
      genres
      episodes
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name              
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

recommended_query = """
query  {
  Page(perPage:15) {
    media( type: ANIME,genre_not_in:["hentai"]) {
      recommendations(sort:RATING_DESC){
        nodes{
          media{
            id
            title{
              english
              romaji
              native
            }
            coverImage{
              medium
              large
            }
            description
            episodes
            trailer{
              site
              id
            }
            
            genres
            averageScore
            popularity
            favourites
            tags {
              name
            }
            startDate {
              year
              month
              day
            }
            endDate {
              year
              month
              day
            }
            status
            nextAiringEpisode {
              timeUntilAiring
              airingAt
              episode
            }
          }
        }
      }
    }
  }
}
"""

anime_characters_query = """
query($id:Int){
  Page {
    media(id:$id, type: ANIME) {
      characters {
        nodes {
          name {
            first
            middle
            last
            full
            native
          }
          image {
            medium
            large
          }
          description
          gender
          dateOfBirth {
            year
            month
            day
          }
          age
          bloodType
          favourites
        }
      }
    }
  }
}
"""


anime_relations_query = """
query ($id: Int) {
  Page(perPage: 20) {
    media(id: $id, sort: POPULARITY_DESC, type: ANIME,genre_not_in:["hentai"]) {
      relations {
        nodes {
          id
          title {
            english
            romaji
            native
          }
          coverImage {
            medium
            large
          }
          description
          episodes
          trailer {
            site
            id
          }
          genres
          averageScore
          popularity
          favourites
          tags {
            name
          }
          startDate {
              year
              month
              day
            }
            endDate {
              year
              month
              day
            }
            status
            nextAiringEpisode {
              timeUntilAiring
              airingAt
              episode
            }
        }
      }
    }
  }
}
"""

airing_schedule_query = """
query ($id: Int) {
  Page {
    media(id: $id, sort: POPULARITY_DESC, type: ANIME) {
      airingSchedule(notYetAired:true){
        nodes{
          airingAt
          timeUntilAiring
          episode
          
        }
      }
    }
  }
}
"""

upcoming_anime_query = """
query ($page: Int) {
  Page(page: $page) {
    pageInfo {
      total
      perPage
      currentPage
      hasNextPage
    }
    media(type: ANIME, status: NOT_YET_RELEASED,sort:POPULARITY_DESC,genre_not_in:["hentai"]) {
      id
      title {
        romaji
        english
      }
      coverImage {
        medium
        large
      }
      trailer {
        site
        id
      }
      popularity
      favourites
      averageScore
      genres
      episodes
      description
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      tags {
        name
      }
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      status
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
    }
  }
}
"""

anime_query = """
query($id:Int){
  Page{
    media(id:$id) {
      id
      title {
        romaji
        english
      }
      nextAiringEpisode {
        timeUntilAiring
        airingAt
        episode
      }
      coverImage {
        extraLarge
      }
      characters(perPage: 5, sort: FAVOURITES_DESC) {
        edges {
          node {
            name {
              full
              
            }
            gender
            dateOfBirth {
              year
              month
              day
            }
            age
            image {
              medium
              large
            }
            description
          }
          voiceActors {
            name {
              full
            }
            image {
              medium
              large
            }
          }
        }
      }
      studios {
        nodes {
          name
          isAnimationStudio
        }
      }
      season
      format
      status
      seasonYear
      description
      genres
      synonyms
      startDate {
        year
        month
        day
      }
      endDate {
        year
        month
        day
      }
      duration
      countryOfOrigin
      averageScore
      popularity
      favourites
      source
      hashtag
      siteUrl
      tags {
        name
        rank
      }
      reviews(sort: SCORE_DESC, perPage: 3) {
        nodes {
          summary
          user {
            name
            avatar {
              medium
              large
            }
          }
        }
      }
      recommendations(sort: RATING_DESC, perPage: 10) {
        nodes {
          mediaRecommendation {
            title {
              romaji
              english
            }
          }
        }
      }
      relations {
        nodes {
          title {
            romaji
            english
            native
          }
        }
      }
      externalLinks {
        url
        site
        icon
      }
      rankings {
        rank
        context
      }
      bannerImage
      episodes
    }
  }
}
"""

# print(search_query)
