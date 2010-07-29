#!/bin/bash
echo "DMoz PL"

python readin.py -f /Users/sebastiankruk/Documents/KnowledgeHives/workshop/projects/OpenVocabulary/dmoz_pl/rdf/ov-taxonomies-dmoz-pl.nt &

echo "DMoz EN"

python readin.py -f /Users/sebastiankruk/Documents/KnowledgeHives/workshop/projects/OpenVocabulary/dmoz_en/rdf/ov-taxonomies-dmoz-all.nt &

echo "OV OpenThesaurus PL"

python readin.py -f /Users/sebastiankruk/Documents/KnowledgeHives/workshop/projects/OpenVocabulary/openthesaurus_pl/rdf/ov-openthesaurus-pl-complete-inscheme-fixed.nt &

echo "WordNet EN"

python readin.py -f /Users/sebastiankruk/Documents/KnowledgeHives/workshop/projects/OpenVocabulary/wordnet_en/src/wn20-full-enh.nt &

