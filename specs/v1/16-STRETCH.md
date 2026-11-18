### Requirement 16: Stretch Features

**User Story:** As a product owner, I want the prototype's extra card features tracked as stretch work, so that they do not delay the core paths.

#### Acceptance Criteria

1. WHERE the stretch features are enabled, THE Backend SHALL store a nullable 0 to 10 integer `progress` and an integer `views_count` defaulting to 0 on Card.
2. WHERE the stretch features are enabled, THE Frontend SHALL show the per-card progress meter, views counter, and the decorative Overview, Notes, and Questions tabs as in the prototype.
3. THE System SHALL build the stretch features only after Requirements 1 to 15 work end-to-end.
