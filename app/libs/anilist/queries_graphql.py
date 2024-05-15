optional_variables = "\
$page:Int,\
$sort:[MediaSort],\
$genre_in:[String],\
$genre_not_in:[String],\
$tag_in:[String],\
$tag_not_in:[String],\
$status_in:[MediaStatus],\
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
search_query = """
query($query:String,%s){
  Page(perPage:15,page:$page){
    pageInfo{
      total
      currentPage
    }
    media(
      search:$query,
      genre_in:$genre_in,
      genre_not_in:$genre_not_in,
      tag_in:$tag_in,
      tag_not_in:$tag_not_in,
      status_in:$status_in,
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
          favourites
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
""" % optional_variables

trending_query = """
query{  
  Page(perPage:15){
    
    media(sort:TRENDING_DESC,type:ANIME){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
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
          favourites
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
    media(sort:FAVOURITES_DESC,type:ANIME){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
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
          favourites
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
    media(sort:SCORE_DESC,type:ANIME){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
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
          favourites
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
    media(sort:POPULARITY_DESC,type:ANIME){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
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
          favourites
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
    media(sort:UPDATED_AT_DESC,type:ANIME){
      id
      title{
        romaji
        english
      }
      coverImage{
        medium
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
          favourites
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
    media( type: ANIME) {
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
    media(id: $id, sort: POPULARITY_DESC, type: ANIME) {
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
    media(type: ANIME, status: NOT_YET_RELEASED,sort:POPULARITY_DESC) {
      id
      title {
        romaji
        english
      }
      coverImage {
        medium
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
          favourites
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
# print(search_query)