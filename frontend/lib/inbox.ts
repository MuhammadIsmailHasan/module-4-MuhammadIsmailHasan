import type { Notification } from "./types";

/** Where a Notification leads (Requirement 28, criterion 5). */
export function hrefFor(n: Notification): string {
  switch (n.type) {
    case "assigned":
    case "deadline":
      return n.board_id && n.card_id ? `/boards/${n.board_id}?card=${n.card_id}` : n.board_id ? `/boards/${n.board_id}` : "/boards";
    case "board_join_requested":
      return n.board_id ? `/boards/${n.board_id}?invite=1` : "/boards";
    case "board_added":
      return n.board_id ? `/boards/${n.board_id}` : "/boards";
    default:
      return "/boards"; // board_join_rejected: the requester has no access to the Board
  }
}

/** One sentence naming the actor and the Board or Card (Requirement 28, criterion 11). Never an Email. */
export function sentenceFor(n: Notification): string {
  const board = n.board_name ?? "a board";
  const actor = n.actor_name ?? "Someone";
  switch (n.type) {
    case "assigned":
      return n.card_title ? `You were assigned “${n.card_title}”` : "A card was assigned to you";
    case "deadline":
      return n.card_title ? `“${n.card_title}” is due today` : "A card is due today";
    case "board_join_requested":
      return `${actor} asked to join “${board}”`;
    case "board_added":
      return `You were added to “${board}”`;
    default:
      return `Your request to join “${board}” was declined`;
  }
}
