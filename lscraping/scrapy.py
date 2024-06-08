import requests

# graphql queries

search_gql = """
query( 
    $search: SearchInput,
    $limit: Int,
    $page: Int,
    $translationType: VaildTranslationTypeEnumType,
    $countryOrigin: VaildCountryOriginEnumType
    ) { 
    shows(  
        search: $search,
        limit: $limit,
        page: $page,
        translationType: $translationType,
        countryOrigin: $countryOrigin
    ) { 
        edges {    
        _id
        name
        availableEpisodes
        __typename
        } 
    }
}
"""

# allanime constants
agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
)
allanime_base = "allanime.day"
allanime_api = f"https://api.{allanime_base}/api"

##allanime referer header
allanime_referer = "https://allanime.to"


search = {"allowAdult": False, "allowUnknown": False, "query": "one piece"}
limit = 40
translationType = "sub"  # dub
countryOrigin = "ALL"
page = 1

variables = {
    "search": search,
    "limit": limit,
    "page": page,
    "translationType": translationType,
    "countryOrigin": countryOrigin,
}

query = search_gql
resp = requests.get(
    allanime_api,
    params={"variables": variables, "query": query},
    headers={"User-Agent": agent, "Referer": allanime_referer},
)

print(resp.json(), resp.status_code)


episodes_list_gql = """
query ($showId: String!) {
    show(_id: $showId) {
        _id availableEpisodesDetail
    }
}
"""
# curl -e "$allanime_refr" -s -G "${allanime_api}/api" --data-urlencode "variables={\"showId\":\"$*\"}" --data-urlencode "query=$episodes_list_gql" -A "$agent" | sed -nE "s|.*$mode\":\[([0-9.\",]*)\].*|\1|p" | sed 's|,|\
