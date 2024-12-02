SEARCH_GQL = """
query (
  $search: SearchInput
  $limit: Int
  $page: Int
  $translationType: VaildTranslationTypeEnumType
  $countryOrigin: VaildCountryOriginEnumType
) {
  shows(
    search: $search
    limit: $limit
    page: $page
    translationType: $translationType
    countryOrigin: $countryOrigin
  ) {
    pageInfo {
      total
    }
    edges {
      _id
      name
      availableEpisodes
      __typename
    }
  }
}
"""


EPISODES_GQL = """\
query (
  $showId: String!
  $translationType: VaildTranslationTypeEnumType!
  $episodeString: String!
) {
  episode(
    showId: $showId
    translationType: $translationType
    episodeString: $episodeString
  ) {
    episodeString
    sourceUrls
    notes
  }
}
"""

SHOW_GQL = """
query ($showId: String!) {
  show(_id: $showId) {
    _id
    name
    availableEpisodesDetail
  }
}
"""
