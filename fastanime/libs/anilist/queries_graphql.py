"""
This module contains all the preset queries for the sake of neatness and convinience
Mostly for internal usage
"""

# TODO: Format the queries
mark_as_read_mutation = """
mutation{
  UpdateUser{
    unreadNotificationCount
  }
}
"""
reviews_query = """
query($id:Int){
  Page{
    pageInfo{
      total
    }
    
    reviews(mediaId:$id){
      summary
      user{
        name
        avatar {
          large
          medium
        }
      }
      body
      
    }
  }
}

"""
notification_query = """
query{
    Page(perPage:5){
        pageInfo {
            total
        }
        notifications(resetNotificationCount:true,type:AIRING) {
            ... on AiringNotification {
                id
                type
                episode
                contexts
                createdAt
                media {
                    id
                    idMal
                    title {
                        romaji
                        english
                    }
                    coverImage{
                        medium
                    }
                }
            }
        }
    }
}

"""

get_medialist_item_query = """
query($mediaId:Int){
    MediaList(mediaId:$mediaId){
        id
    }
}
"""

delete_list_entry_query = """
mutation($id:Int){
    DeleteMediaListEntry(id:$id){
        deleted

    }
}
"""

get_logged_in_user_query = """
query{
  Viewer{
    id
    name
    bannerImage
    avatar {
      large
      medium
    }
    
  }
}
"""

media_list_mutation = """
mutation($mediaId:Int,$scoreRaw:Int,$repeat:Int,$progress:Int,$status:MediaListStatus){
  SaveMediaListEntry(mediaId:$mediaId,scoreRaw:$scoreRaw,progress:$progress,repeat:$repeat,status:$status){
    id
    status
    mediaId
    score
    progress
    repeat
    startedAt {
      year
      month
      day
    }
    completedAt {
      year
      month
      day
    }

  }
}
"""

media_list_query = """
query ($userId: Int, $status: MediaListStatus,$type:MediaType) {
  Page {
    pageInfo {
        currentPage
        total
    }
    mediaList(userId: $userId, status: $status, type: $type) {
      mediaId
      
      media {
        id
        idMal
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
        description
        mediaListEntry{
        id
        progress
        }
        nextAiringEpisode {
          timeUntilAiring
          airingAt
          episode
        }
      }
      status
      progress
      score
      repeat
      notes
      startedAt {
        year
        month
        day
      }
      completedAt {
        year
        month
        day
      }
      createdAt
      
    }
  }
}
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
$endDate_lesser:FuzzyDateInt,\
$type:MediaType\
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
      type:$type
      )
    {
      id
        idMal
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
        mediaListEntry{
        id
        progress
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
query($type:MediaType){  
  Page(perPage:15){
    
    media(sort:TRENDING_DESC,type:$type,genre_not_in:["hentai"]){
      id
        idMal
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
        mediaListEntry{
        id
        progress
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
query($type:MediaType){
  Page(perPage:15){    
    media(sort:FAVOURITES_DESC,type:$type,genre_not_in:["hentai"]){
      id
        idMal
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
        mediaListEntry{
        id
        progress
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
query($type:MediaType){
  Page(perPage:15){
    media(sort:SCORE_DESC,type:$type,genre_not_in:["hentai"]){
      id
        idMal
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
        mediaListEntry{
        id
        progress
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
query($type:MediaType){  
  Page(perPage:15){
    media(sort:POPULARITY_DESC,type:$type,genre_not_in:["hentai"]){
      id
        idMal
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
        mediaListEntry{
        id
        progress
        }
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
query($type:MediaType){
  Page(perPage:15){
    media(sort:UPDATED_AT_DESC,type:$type,averageScore_greater:50,genre_not_in:["hentai"],status:RELEASING){
      id
        idMal
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
        mediaListEntry{
        id
        progress
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
query($type:MediaType){
  Page(perPage:15) {
    media( type: $type,genre_not_in:["hentai"]) {
      recommendations(sort:RATING_DESC){
        nodes{
          media{
            id
        idMal
            title{
              english
              romaji
              native
            }
            coverImage{
              medium
              large
            }
            mediaListEntry{
                id
                progress
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
query($id:Int,$type:MediaType){
  Page {
    media(id:$id, type: $type) {
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
query ($id: Int,$type:MediaType) {
  Page(perPage: 20) {
    media(id: $id, sort: POPULARITY_DESC, type: $type,genre_not_in:["hentai"]) {
      relations {
        nodes {
          id
        idMal
          title {
            english
            romaji
            native
          }
          coverImage {
            medium
            large
          }
        mediaListEntry{
        id
        progress
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
query ($id: Int,$type:MediaType) {
  Page {
    media(id: $id, sort: POPULARITY_DESC, type: $type) {
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
query ($page: Int,$type:MediaType) {
  Page(page: $page) {
    pageInfo {
      total
      perPage
      currentPage
      hasNextPage
    }
    media(type: $type, status: NOT_YET_RELEASED,sort:POPULARITY_DESC,genre_not_in:["hentai"]) {
      id
        idMal
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
              mediaListEntry{
        id
        progress
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
        idMal
      title {
        romaji
        english
      }
              mediaListEntry{
        id
        progress
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
