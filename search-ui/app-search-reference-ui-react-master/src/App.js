import React from "react";

import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

import {
  ErrorBoundary,
  Facet,
  SearchProvider,
  SearchBox,
  Results,
  PagingInfo,
  ResultsPerPage,
  Paging,
  Sorting,
  WithSearch
} from "@elastic/react-search-ui";
import { Layout } from "@elastic/react-search-ui-views";
import "@elastic/react-search-ui-views/lib/styles/styles.css";


const connector = new ElasticsearchAPIConnector({
  host: "http://localhost:9200",
  index: "cv-transcriptions"
});

const getFacetFields = () => ["age", "gender", "accent", "duration"];

const config = {
  searchQuery: {
    search_fields: {
      generated_text: {
        weight: 2
      }
    },
    result_fields: {
      generated_text: {
        snippet: {
          size: 100,
          fallback: true
        }
      },
      duration: { raw: {} },
      age: { raw: {} },
      gender: { raw: {} },
      accent: { raw: {} }
    },
    disjunctiveFacets: ["age", "gender", "accent"],
    facets: {
      age: { type: "value", size: 10 },
      gender: { type: "value", size: 10 },
      accent: { type: "value", size: 10 },
      duration: {
        type: "range",
        ranges: [
          { from: 0, to: 2, name: "0–2 sec" },
          { from: 2, to: 5, name: "2–5 sec" },
          { from: 5, to: 10, name: "5–10 sec" },
          { from: 10, name: "10+ sec" }
        ]
      }
    }
  },
  // autocompleteQuery:{
  //   suggestions: {
  //     size: 5,
  //     types:{
  //       documents: {
  //         fields: ["generated_text"]
  //       }
  //     }
  //   }
  // },
  apiConnector: connector,
  alwaysSearchOnInitialLoad: true
};

export default function App() {
  return (
    <SearchProvider config={config}>
      <WithSearch mapContextToProps={({ wasSearched }) => ({ wasSearched })}>
        {({ wasSearched }) => {
          return (
            <div className="App">
              <ErrorBoundary>
                <Layout
                  header={<SearchBox />}
                  sideContent={
                    <div>
                      {getFacetFields().map(field => (
                        <Facet key={field} field={field} label={field} />
                      ))}
                    </div>
                  }
                  bodyContent={
                    <Results
                      titleField="generated_text"
                      shouldTrackClickThrough={false}
                    />
                  }
                  bodyHeader={
                    <>
                      {wasSearched && <PagingInfo />}
                      {wasSearched && <ResultsPerPage />}
                    </>
                  }
                  bodyFooter={<Paging />}
                />
              </ErrorBoundary>
            </div>
          );
        }}
      </WithSearch>
    </SearchProvider>
  );
}