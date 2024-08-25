from sqlmodel import create_engine, Session, select
from fpl_dashboard.data.database_model import *
from fpl_dashboard.data.fpl_api_handler import FPLAPIHandler, FPLAPIEndpoint
engine = create_engine("sqlite:///fpl_dashboard.db", echo=False)
session = Session(engine)


def get_top_players_by_pos_and_metric(pos: list, metric: str):
    query = select(Element)\
            .where(
                Element.player_position.has(
                    ElementType.singular_name_short.in_(pos)
                )
            ).order_by(
                getattr(Element, metric).desc()
            ).limit(10)

    top_players = session.exec(query).all()

    return top_players

def players_adjusted_ownership(positions):
    players = session.exec(select(Element).where(Element.player_position.has(ElementType.singular_name_short.in_(positions)))).all()
    mu = sum([player.total_points for player in players]) / len(players)
    sigma = sum([((player.total_points - mu) ** 2) for player in players]) / len(players)
    index = [(player, round((player.total_points - mu) / sigma * (1-player.selected_by_percent/100)*player.total_points,2)) for player in players]

    return sorted(index, key=lambda x: x[1], reverse=True)[:10]

def players_adjusted_consistency(positions):
    players = session.exec(select(Element).where(Element.player_position.has(ElementType.singular_name_short.in_(positions)))).all()

    return sorted([(player, round(player.points_adjusted_for_consistency,2)) for player in players], key=lambda x: x[1], reverse=True)[:10]

def players_adjusted_consistency_and_ownership(positions):
    players = session.exec(select(Element).where(Element.player_position.has(ElementType.singular_name_short.in_(positions)))).all()

    return sorted([(player, round(player.points_adjusted_for_consistency*(1-player.selected_by_percent/100),2)) for player in players], key=lambda x: x[1], reverse=True)[:10]

if __name__ == "__main__":
    with session:    
        positions = ["DEF", "GKP", "MID", "FWD"]
        for pos in positions:
            print(f"\nTop players {pos}:")
            top_players = get_top_players_by_pos_and_metric([pos], "total_points")

            for player in top_players:
                print(player.player_position.singular_name_short, player.player_team.short_name, player.total_points, player.web_name)

            print("\nPlayer points adjusted for relative performance and ownership:")
            for player in players_adjusted_ownership([pos]):
                print(player[0].player_position.singular_name_short, player[0].player_team.short_name, player[0].total_points, player[0].web_name, player[1])

            print("\nPlayer points adjusted for consistency:")
            for player in players_adjusted_consistency([pos]):
                print(player[0].player_position.singular_name_short, player[0].player_team.short_name, player[0].total_points, player[0].web_name, player[1])

            print("\nPlayer points adjusted for consistency and ownership:")
            for player in players_adjusted_consistency_and_ownership([pos]):
                print(player[0].player_position.singular_name_short, player[0].player_team.short_name, player[0].total_points, player[0].web_name, player[1])