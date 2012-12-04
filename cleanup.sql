DELETE FROM ov_triple WHERE subject_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);
DELETE FROM ov_triple WHERE object_id IN (SELECT id FROM ov_uri WHERE uri LIKE '$CONTEXT_URI_PATTERN%');

DELETE FROM ov_entryreference WHERE subject_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);
DELETE FROM ov_entryreference WHERE object_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);

DELETE FROM ov_entry_types WHERE entry_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);
DELETE FROM ov_entry_types WHERE uri_id IN (SELECT id FROM ov_uri WHERE uri LIKE '$CONTEXT_URI_PATTERN%');

DELETE FROM ov_entry_words WHERE from_entry_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);
DELETE FROM ov_entry_words WHERE to_entry_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);

DELETE FROM ov_entry_word_senses WHERE from_entry_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);
DELETE FROM ov_entry_word_senses WHERE to_entry_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);

DELETE FROM ov_entry_meanings WHERE from_entry_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);
DELETE FROM ov_entry_meanings WHERE to_entry_id IN (SELECT id FROM ov_entry WHERE context_id = $CONTEXT_ID);

DELETE FROM ov_uri WHERE uri LIKE '$CONTEXT_URI_PATTERN%';
DELETE FROM ov_entry WHERE context_id = $CONTEXT_ID;
DELETE FROM ov_context_tags WHERE context_id = $CONTEXT_ID;
DELETE FROM ov_context WHERE id = $CONTEXT_ID;
